// Small session store: the last answer is kept so an evidence page can be opened from its link.
const KEY = 'lastAnswer'

export function saveAnswer(answer) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(answer))
  } catch {
    /* storage can be unavailable; the evidence page then falls back to the Ask page */
  }
}

export function loadAnswer() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY) || 'null')
  } catch {
    return null
  }
}
