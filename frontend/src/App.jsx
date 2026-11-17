import { useEffect, useState } from 'react'
import { ApiError, getJson, hasToken, setToken } from './api.js'
import { go, useRoute } from './router.js'
import SignIn from './SignIn.jsx'
import Ask from './pages/Ask.jsx'
import Evidence from './pages/Evidence.jsx'
import Papers from './pages/Papers.jsx'
import Compare from './pages/Compare.jsx'
import Admin from './pages/Admin.jsx'
import Audit from './pages/Audit.jsx'
import { Notice } from './ui.jsx'
import ErrorBoundary from './ErrorBoundary.jsx'
import Sidebar from './Sidebar.jsx'

function pick(path, user) {
  const login = user.login
  if (path.startsWith('/evidence/')) return <Evidence id={decodeURIComponent(path.slice('/evidence/'.length))} />
  if (path === '/papers') return <Papers />
  if (path === '/compare') return <Compare key="new" login={login} />
  if (path.startsWith('/compare/')) return <Compare key={path} login={login} chatId={path.slice('/compare/'.length)} />
  if (path.startsWith('/chat/')) return <Ask key={path} login={login} chatId={path.slice('/chat/'.length)} />
  if (path === '/admin' && user.role === 'ADMIN') return <Admin />
  if (path === '/admin/audit' && user.role === 'ADMIN') return <Audit />
  return <Ask key="new" login={login} />
}

function Shell({ user, onSignOut }) {
  const path = useRoute()
  const [sidebarExpanded, setSidebarExpanded] = useState(true)
  const links = [
    ['/', 'Ask'],
    ['/papers', 'Papers'],
    ['/compare', 'Compare'],
    ...(user.role === 'ADMIN' ? [['/admin', 'Admin']] : []),
  ]
  const section = (to) => (to === '/' ? path === '/' || path.startsWith('/evidence') || path.startsWith('/chat/') : path.startsWith(to))
  // Recent chats belong with the conversation pages, not the paper list or admin screens.
  const showSidebar = !path.startsWith('/papers') && !path.startsWith('/admin')
  return (
    <>
      <header className="topbar">
        <span className="brand">ResearchIQ</span>
        <nav className="nav" aria-label="Main">
          {links.map(([to, name]) => (
            <a key={to} href={`#${to}`} aria-current={section(to) ? 'page' : undefined}>
              {name}
            </a>
          ))}
        </nav>
        <div className="who">
          <span>
            {user.login} · {user.role === 'ADMIN' ? 'Admin' : 'Reader'}
          </span>
          <button className="linkbtn" onClick={onSignOut}>
            Sign out
          </button>
        </div>
      </header>
      <div className={`layout ${!showSidebar ? 'solo' : sidebarExpanded ? '' : 'sidebar-collapsed'}`}>
        {showSidebar && (
          <div className="sidebar-shell">
            <button
              type="button"
              className="sidebar-toggle"
              aria-expanded={sidebarExpanded}
              aria-controls="recent-chats"
              aria-label={sidebarExpanded ? 'Collapse recent chats' : 'Expand recent chats'}
              onClick={() => setSidebarExpanded((expanded) => !expanded)}
            >
              <span aria-hidden="true" />
            </button>
            <div className="sidebar-viewport" inert={sidebarExpanded ? undefined : ''} aria-hidden={!sidebarExpanded}>
              <Sidebar login={user.login} path={path} />
            </div>
          </div>
        )}
        <main><ErrorBoundary key={path}>{pick(path, user)}</ErrorBoundary></main>
      </div>
      <p className="footnote">Answers are written by an AI from the papers and checked in code. Open each citation to read the source.</p>
    </>
  )
}

export default function App() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(hasToken())
  const [problem, setProblem] = useState('')
  const [expired, setExpired] = useState(false)

  async function loadUser() {
    try {
      setUser(await getJson('/me'))
      setProblem('')
    } catch (e) {
      setUser(null)
      if (e instanceof ApiError && e.status === 0) setProblem(e.message)
    } finally {
      setChecking(false)
    }
  }

  function signOut() {
    setToken('')
    setUser(null)
    go('/')
  }

  useEffect(() => {
    if (hasToken()) loadUser()
    const onExpired = () => {
      setUser(null)
      setExpired(true)
    }
    window.addEventListener('session-expired', onExpired)
    return () => window.removeEventListener('session-expired', onExpired)
  }, [])

  if (checking) return <main><p className="muted">Loading…</p></main>
  if (!user) {
    return (
      <>
        <SignIn expired={expired} onSignedIn={() => { setExpired(false); setChecking(true); loadUser() }} />
        {problem && <Notice error>{problem}</Notice>}
      </>
    )
  }
  return <Shell user={user} onSignOut={signOut} />
}
