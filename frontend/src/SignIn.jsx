import { useState } from 'react'
import { ApiError, postJson, setToken } from './api.js'
import { Notice } from './ui.jsx'

// Demo buttons exist only when the demo variables are set; production builds leave them unset.
const env = import.meta.env
const DEMOS = [
  { role: 'Admin', login: env.VITE_DEMO_ADMIN_LOGIN, password: env.VITE_DEMO_ADMIN_PASSWORD },
  { role: 'Reader', login: env.VITE_DEMO_USER_LOGIN, password: env.VITE_DEMO_USER_PASSWORD },
].filter((d) => d.login && d.password)

export default function SignIn({ onSignedIn, expired }) {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const result = await postJson('/auth/login', { login, password })
      setToken(result.access_token)
      onSignedIn()
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Sign-in failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="signin">
      <div>
        <h1>ResearchIQ</h1>
        <p className="lede">
          Ask a question across the collection and see which paper, page and figure each statement
          comes from. If the evidence is not there, it says so.
        </p>
      </div>
      <form onSubmit={submit} aria-label="Sign in">
        <h2>Sign in</h2>
        <div>
          <label htmlFor="login">Login</label>
          <input id="login" type="text" autoComplete="username" value={login} onChange={(e) => setLogin(e.target.value)} />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <Notice>{expired && !error ? 'Your session ended. Please sign in again.' : ''}</Notice>
        <Notice error>{error}</Notice>
        <button className="primary" type="submit" disabled={busy || !login || !password}>
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
        {DEMOS.length > 0 && (
          <div>
            <p className="small muted">Demo: fills the form, then press Sign in.</p>
            <div className="demo">
              {DEMOS.map((d) => (
                <button
                  key={d.role}
                  type="button"
                  className="secondary"
                  onClick={() => {
                    setLogin(d.login)
                    setPassword(d.password)
                  }}
                >
                  Demo: {d.role}
                </button>
              ))}
            </div>
          </div>
        )}
      </form>
    </div>
  )
}
