import { useEffect, useState } from 'react'

// Recent chats live in this browser only, one list per signed-in login. The API keeps no history,
// so nothing here is shared between devices or readers.
const MAX_CHATS = 20
const keyFor = (login) => `chats:${login}`

function read(login) {
  try {
    const list = JSON.parse(localStorage.getItem(keyFor(login)) || '[]')
    return Array.isArray(list) ? list : []
  } catch {
    return []
  }
}

function write(login, chats) {
  let list = chats
  for (;;) {
    try {
      localStorage.setItem(keyFor(login), JSON.stringify(list))
      break
    } catch {
      // Storage full or unavailable: drop the oldest chat and retry.
      if (list.length <= 1) break
      list = list.slice(0, -1)
    }
  }
  window.dispatchEvent(new Event('chats-changed'))
}

export function getChat(login, id) {
  return read(login).find((c) => c.id === id) || null
}

// kind: 'ask' | 'compare'. Newest first, oldest dropped past the cap.
export function addChat(login, chat) {
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  write(login, [{ ...chat, id, at: Date.now() }, ...read(login)].slice(0, MAX_CHATS))
  return id
}

export function removeChat(login, id) {
  write(login, read(login).filter((c) => c.id !== id))
}

export function clearChats(login) {
  write(login, [])
}

export function useChats(login) {
  const [chats, setChats] = useState(() => read(login))
  useEffect(() => {
    const refresh = () => setChats(read(login))
    refresh()
    window.addEventListener('chats-changed', refresh)
    window.addEventListener('storage', refresh)
    return () => {
      window.removeEventListener('chats-changed', refresh)
      window.removeEventListener('storage', refresh)
    }
  }, [login])
  return chats
}

export function ago(ms) {
  const minutes = Math.round((Date.now() - ms) / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} h ago`
  return new Date(ms).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })
}
