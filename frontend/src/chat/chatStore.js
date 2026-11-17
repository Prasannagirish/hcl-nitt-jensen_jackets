// Chat threads, stored in the browser and kept separate for each signed-in user.
//
// Contract for the recent-chats sidebar:
//   listChats()        -> [{ id, title, updatedAt, turnCount }], newest first
//   getChat(id)        -> { id, title, createdAt, updatedAt, turns: [...] } or null (read-only)
//   hasPending(id)     -> true while a question of that chat is being answered (read-only)
//   newChat()          -> id (the new chat also becomes the active one)
//   activeChatId() / setActiveChat(id)
//   deleteChat(id)
//   window event 'chats-changed' fires after every change.
// A turn is { id, question, status: 'pending' | 'done' | 'error', answer, error, startedAt }.
import { postJson } from '../api.js'
import { loadAnswer } from '../store.js'

const MAX_CHATS = 50
// Turns whose request is running in this page right now. Kept on globalThis so that a hot reload
// of this module (which re-runs this file) does not forget requests that are still in progress.
const inFlight = (globalThis.__researchiqInFlight ??= new Set())
// A pending turn is only called interrupted after this long. It must exceed the request timeout in
// api.js (90 s), so a question still running here, in another tab, or across a reload is never
// misreported.
const GRACE_MS = 120000

// True while the answer may still arrive: running in this page, or started recently elsewhere.
function isLive(turn) {
  return inFlight.has(turn.id) || Date.now() - (turn.startedAt || 0) < GRACE_MS
}

function owner() {
  // The token's "sub" claim only namespaces the storage. The server still checks every request.
  try {
    const token = sessionStorage.getItem('token') || ''
    return JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))).sub || 'anon'
  } catch {
    return 'anon'
  }
}

const storageKey = () => `researchiq.chats.${owner()}`

function read() {
  try {
    const data = JSON.parse(localStorage.getItem(storageKey()) || 'null')
    return data && data.chats ? data : { activeId: '', chats: {} }
  } catch {
    return { activeId: '', chats: {} }
  }
}

function write(data) {
  const chats = Object.values(data.chats).sort((a, b) => b.updatedAt - a.updatedAt)
  for (const old of chats.slice(MAX_CHATS)) delete data.chats[old.id]
  // Answers carry the cited text, so storage can fill up: drop the oldest chats until it fits.
  for (let tries = 0; tries < 20; tries += 1) {
    try {
      localStorage.setItem(storageKey(), JSON.stringify(data))
      break
    } catch {
      const oldest = Object.values(data.chats).sort((a, b) => a.updatedAt - b.updatedAt)[0]
      if (!oldest || oldest.id === data.activeId) break
      delete data.chats[oldest.id]
    }
  }
  window.dispatchEvent(new Event('chats-changed'))
}

function makeId() {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

// A turn left "pending" by a page that was closed will never finish: show it as interrupted.
// This only changes the copy that is returned; reading never writes to storage.
function settle(chat) {
  const turns = chat.turns.map((t) =>
    t.status === 'pending' && !isLive(t)
      ? { ...t, status: 'error', error: 'This question was interrupted. Ask it again.' }
      : t,
  )
  return { ...chat, turns }
}

export function listChats() {
  // A chat with no question yet is not worth listing.
  return Object.values(read().chats)
    .filter((c) => c.turns.length > 0)
    .sort((a, b) => b.updatedAt - a.updatedAt)
    .map((c) => ({ id: c.id, title: c.title, updatedAt: c.updatedAt, turnCount: c.turns.length }))
}

// Read-only: safe to call while rendering.
export function getChat(id) {
  const chat = read().chats[id]
  return chat ? settle(chat) : null
}

// Read-only: true while a question of this chat may still be answered (this page or another tab).
export function hasPending(id) {
  const chat = read().chats[id]
  return Boolean(chat?.turns.some((t) => t.status === 'pending' && isLive(t)))
}

export function activeChatId() {
  const data = read()
  return data.chats[data.activeId] ? data.activeId : ''
}

export function setActiveChat(id) {
  const data = read()
  if (!data.chats[id] || data.activeId === id) return
  data.activeId = id
  write(data)
}

export function newChat() {
  const data = read()
  const id = makeId()
  const now = Date.now()
  data.chats[id] = { id, title: 'New chat', createdAt: now, updatedAt: now, turns: [] }
  data.activeId = id
  write(data)
  return id
}

export function deleteChat(id) {
  const data = read()
  delete data.chats[id]
  if (data.activeId === id) data.activeId = ''
  write(data)
}

function changeTurn(chatId, turnId, change) {
  const data = read()
  const turn = data.chats[chatId]?.turns.find((t) => t.id === turnId)
  if (!turn) return
  Object.assign(turn, change)
  data.chats[chatId].updatedAt = Date.now()
  write(data)
}

// Ask one question in a chat. The answer is written into the store when it arrives, so it is kept
// even if the reader has moved to another page or chat by then.
export async function askInChat(chatId, question) {
  const data = read()
  const chat = data.chats[chatId]
  if (!chat) return
  const turn = { id: makeId(), question, status: 'pending', answer: null, error: '', startedAt: Date.now() }
  chat.turns.push(turn)
  if (chat.turns.length === 1) chat.title = question.slice(0, 60)
  chat.updatedAt = Date.now()
  write(data)
  inFlight.add(turn.id)
  try {
    const answer = await postJson('/query', { question })
    changeTurn(chatId, turn.id, { status: 'done', answer })
  } catch (error) {
    changeTurn(chatId, turn.id, { status: 'error', error: error.message || 'The question could not be answered.' })
  } finally {
    inFlight.delete(turn.id)
  }
}

export function removeTurn(chatId, turnId) {
  const data = read()
  const chat = data.chats[chatId]
  if (!chat) return
  chat.turns = chat.turns.filter((t) => t.id !== turnId)
  write(data)
}

// Evidence for the source page: any turn of the active chat, else the last comparison answer.
export function findEvidence(evidenceId) {
  const chat = getChat(activeChatId())
  const answers = (chat?.turns ?? []).map((t) => t.answer).filter(Boolean).reverse()
  answers.push(loadAnswer())
  for (const answer of answers) {
    const found = answer?.evidence.find((e) => e.evidence_id === evidenceId)
    if (found) return found
  }
  return null
}
