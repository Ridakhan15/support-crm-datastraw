/**
 * Centralized API client. Every network call in the app goes through here,
 * so components never call fetch() directly and error handling is consistent.
 */
const BASE_URL =
  import.meta.env.VITE_API_URL ||
  'https://support-crm-datastraw-backend.onrender.com'/** Thrown for any non-2xx response. Carries the parsed error detail when available. */
export class ApiError extends Error {
  constructor(message, status, detail) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    // fetch() itself throws on network failure (server down, no connection, CORS block)
    throw new ApiError('Could not reach the server. Check your connection and try again.', 0, null)
  }

  let body = null
  const text = await response.text()
  if (text) {
    try {
      body = JSON.parse(text)
    } catch {
      body = null // non-JSON body (e.g. an HTML 502 page from a misconfigured host)
    }
  }

  if (!response.ok) {
    throw new ApiError(messageFor(response.status, body), response.status, body?.detail)
  }
  return body
}

/** Turn a backend error payload into one readable sentence for toasts/banners. */
function messageFor(status, body) {
  const detail = body?.detail
  if (Array.isArray(detail)) {
    // 422 validation errors: [{ field, message }, ...]
    return detail.map((e) => (e.field ? `${e.field}: ${e.message}` : e.message)).join(', ')
  }
  if (typeof detail === 'string') return detail
  if (status === 404) return 'Not found.'
  if (status >= 500) return 'Something went wrong on our end. Please try again.'
  return 'Something went wrong. Please try again.'
}

export const api = {
  createTicket: (data) => request('/api/tickets', { method: 'POST', body: JSON.stringify(data) }),

  listTickets: ({ status, priority, search } = {}) => {
    const params = new URLSearchParams()
    if (status && status !== 'All') params.set('status', status)
    if (priority) params.set('priority', priority)
    if (search) params.set('search', search)
    const qs = params.toString()
    return request(`/api/tickets${qs ? `?${qs}` : ''}`)
  },

  getStats: () => request('/api/tickets/stats'),

  getNeedsAttention: () => request('/api/tickets/needs-attention'),

  getTicket: (ticketId) => request(`/api/tickets/${encodeURIComponent(ticketId)}`),

  updateTicket: (ticketId, data) =>
    request(`/api/tickets/${encodeURIComponent(ticketId)}`, { method: 'PUT', body: JSON.stringify(data) }),
}
