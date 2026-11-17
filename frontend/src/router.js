import { useEffect, useState } from 'react'

// Hash routes: every page has its own URL, so the browser Back button and pasted links work.
function currentPath() {
  return window.location.hash.replace(/^#/, '') || '/'
}

export function useRoute() {
  const [path, setPath] = useState(currentPath())
  useEffect(() => {
    const onChange = () => setPath(currentPath())
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return path
}

export function go(path) {
  window.location.hash = path
}

// Count navigations made inside the app. document.referrer only describes the first page load,
// so it cannot tell whether going back would stay in the app.
let navigations = 0
window.addEventListener('hashchange', () => {
  navigations += 1
})

// Back returns to the page the reader came from; a directly opened link falls back to the list.
export function goBack(fallback) {
  if (navigations > 0) {
    navigations -= 1
    window.history.back()
  } else {
    go(fallback)
  }
}
