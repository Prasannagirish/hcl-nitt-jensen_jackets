// All calls to the API. A failure always becomes an ApiError with a message a reader can act on.
const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const TIMEOUT_MS = 90000 // a question can take up to about 30 seconds; give up well after that
let token = sessionStorage.getItem('token') || ''

export function setToken(value) {
  token = value
  if (value) sessionStorage.setItem('token', value)
  else sessionStorage.removeItem('token')
}

export function hasToken() {
  return Boolean(token)
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

function describe(body) {
  if (body.detail === 'Invalid request') {
    return (body.errors || []).map((e) => `${e.field}: ${e.problem}`).join('; ')
  }
  return body.detail || 'Something went wrong.'
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`
  let response
  try {
    response = await fetch(BASE + path, { ...options, headers, signal: AbortSignal.timeout(TIMEOUT_MS) })
  } catch (error) {
    if (error.name === 'TimeoutError') {
      throw new ApiError(0, 'The server took too long to answer. Try again in a moment.')
    }
    throw new ApiError(0, 'Cannot reach the server. Start the API (make serve) and try again.')
  }
  if (response.status === 401 && token) {
    setToken('')
    window.dispatchEvent(new Event('session-expired'))
  }
  if (!response.ok) {
    let message = 'Something went wrong.'
    try {
      message = describe(await response.json())
    } catch {
      /* the body was not JSON; keep the generic message */
    }
    throw new ApiError(response.status, message)
  }
  return response
}

export async function getJson(path) {
  return (await request(path)).json()
}

export async function postJson(path, body) {
  const options = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }
  return (await request(path, options)).json()
}

export async function postForm(path, form) {
  return (await request(path, { method: 'POST', body: form })).json()
}

// Images need the bearer token, so they are fetched and shown from a local object URL.
export async function imageUrl(path) {
  const response = await request(path)
  return URL.createObjectURL(await response.blob())
}
