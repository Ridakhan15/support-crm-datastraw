import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Send } from 'lucide-react'
import { api, ApiError } from '../services/api.js'
import { useToast } from '../components/Toast.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import PriorityBadge from '../components/PriorityBadge.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'

const STATUSES = ['Open', 'In Progress', 'Closed']

function formatDateTime(iso) {
  return new Date(iso).toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
  })
}

export default function TicketDetails() {
  const { ticketId } = useParams()
  const { showToast } = useToast()

  const [ticket, setTicket] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updatingStatus, setUpdatingStatus] = useState(false)
  const [noteText, setNoteText] = useState('')
  const [addingNote, setAddingNote] = useState(false)

  function load() {
    setLoading(true)
    setError(null)
    api
      .getTicket(ticketId)
      .then(setTicket)
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Failed to load ticket.'))
      .finally(() => setLoading(false))
  }

  useEffect(load, [ticketId])

  async function handleStatusChange(newStatus) {
    if (newStatus === ticket.status) return
    setUpdatingStatus(true)
    try {
      await api.updateTicket(ticketId, { status: newStatus })
      load() // refresh from the server so status + updated_at + badge stay in sync
      showToast(`Status updated to ${newStatus}.`)
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Failed to update status.', 'error')
    } finally {
      setUpdatingStatus(false)
    }
  }

  async function handleAddNote(e) {
    e.preventDefault()
    if (!noteText.trim()) return
    setAddingNote(true)
    try {
      await api.updateTicket(ticketId, { notes: noteText.trim() })
      setNoteText('')
      load()
      showToast('Note added.')
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Failed to add note.', 'error')
    } finally {
      setAddingNote(false)
    }
  }

  if (loading) return <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6"><LoadingState rows={3} /></div>
  if (error) return <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6"><ErrorState message={error} onRetry={load} /></div>
  if (!ticket) return null

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <nav aria-label="Breadcrumb" className="mb-2 text-sm text-slate-500">
        <Link to="/" className="hover:underline">Dashboard</Link>
        <span className="mx-1.5">/</span>
        <span className="text-slate-700">{ticket.ticket_id}</span>
      </nav>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-slate-900">{ticket.ticket_id}</h1>
        <div className="flex items-center gap-2">
          <PriorityBadge priority={ticket.priority} />
          <StatusBadge status={ticket.status} />
        </div>
      </div>

      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-500">Customer</h2>
        <p className="mt-1 text-slate-900">{ticket.customer_name}</p>
        <p className="text-sm text-slate-500">{ticket.customer_email}</p>

        <h2 className="mt-4 text-sm font-semibold text-slate-500">Subject</h2>
        <p className="mt-1 text-slate-900">{ticket.subject}</p>

        <h2 className="mt-4 text-sm font-semibold text-slate-500">Description</h2>
        <p className="mt-1 whitespace-pre-wrap text-slate-700">{ticket.description}</p>

        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-1 text-sm text-slate-500">
          <span>Created {formatDateTime(ticket.created_at)}</span>
          <span>Last updated {formatDateTime(ticket.updated_at)}</span>
        </div>
      </section>

      <section className="mt-4 rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-500">Update Status</h2>
        <div role="group" aria-label="Update status" className="mt-2 flex flex-wrap gap-2">
          {STATUSES.map((s) => (
            <button
              key={s}
              type="button"
              disabled={updatingStatus}
              onClick={() => handleStatusChange(s)}
              aria-pressed={ticket.status === s}
              className={`rounded-md border px-3 py-1.5 text-sm font-medium disabled:opacity-60 ${
                ticket.status === s
                  ? 'border-brand-600 bg-brand-600 text-white'
                  : 'border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </section>

      <section className="mt-4 rounded-lg border border-slate-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-slate-500">Activity / Notes</h2>

        {ticket.notes.length === 0 ? (
          <p className="mt-2 text-sm text-slate-400">No notes yet.</p>
        ) : (
          <ul className="mt-3 space-y-3">
            {ticket.notes.map((note) => (
              <li key={note.id} className="rounded-md bg-slate-50 p-3 text-sm">
                <p className="text-slate-800">{note.note_text}</p>
                <p className="mt-1 text-xs text-slate-400">{formatDateTime(note.created_at)}</p>
              </li>
            ))}
          </ul>
        )}

        <form onSubmit={handleAddNote} className="mt-4 flex gap-2">
          <label htmlFor="note-input" className="sr-only">Add a note</label>
          <input
            id="note-input"
            type="text"
            value={noteText}
            onChange={(e) => setNoteText(e.target.value)}
            placeholder="Add a note…"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm focus-visible:border-brand-500"
          />
          <button
            type="submit"
            disabled={addingNote || !noteText.trim()}
            className="inline-flex items-center gap-1.5 rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Send className="h-3.5 w-3.5" aria-hidden="true" />
            Add Note
          </button>
        </form>
      </section>
    </div>
  )
}
