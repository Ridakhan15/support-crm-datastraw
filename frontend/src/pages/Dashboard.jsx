import { useEffect, useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../services/api.js'
import StatCard from '../components/StatCard.jsx'
import SearchBar from '../components/SearchBar.jsx'
import StatusFilter from '../components/StatusFilter.jsx'
import TicketTable from '../components/TicketTable.jsx'
import EmptyState from '../components/EmptyState.jsx'
import LoadingState from '../components/LoadingState.jsx'
import ErrorState from '../components/ErrorState.jsx'
import PriorityBadge from '../components/PriorityBadge.jsx'

// How long to wait after the user stops typing before searching, so we don't
// fire a request on every keystroke.
const SEARCH_DEBOUNCE_MS = 350

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [attention, setAttention] = useState([])
  const [tickets, setTickets] = useState([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('All')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    api.getStats().then(setStats).catch(() => {}) // stat failures don't block the page
    api.getNeedsAttention().then(setAttention).catch(() => {})
  }, [reloadKey])

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true)
      setError(null)
      api
        .listTickets({ status, search })
        .then(setTickets)
        .catch((err) => setError(err instanceof ApiError ? err.message : 'Failed to load tickets.'))
        .finally(() => setLoading(false))
    }, SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [status, search, reloadKey])

  const retry = () => setReloadKey((k) => k + 1)

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-semibold text-slate-900">Support Dashboard</h1>

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Tickets" value={stats?.total ?? '—'} />
        <StatCard label="Open" value={stats?.open ?? '—'} accent="text-blue-600" />
        <StatCard label="In Progress" value={stats?.in_progress ?? '—'} accent="text-amber-600" />
        <StatCard label="Closed" value={stats?.closed ?? '—'} accent="text-slate-500" />
      </div>

      {attention.length > 0 && (
        <div className="mt-6 rounded-lg border border-rose-200 bg-rose-50 p-4">
          <div className="flex items-center gap-2 text-rose-800">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" />
            <h2 className="text-sm font-semibold">Needs Attention</h2>
          </div>
          <ul className="mt-2 divide-y divide-rose-100">
            {attention.map((t) => (
              <li key={t.ticket_id} className="flex items-center justify-between gap-3 py-2 text-sm">
                <Link to={`/tickets/${t.ticket_id}`} className="min-w-0 flex-1 truncate text-slate-800 hover:underline">
                  <span className="font-medium">{t.ticket_id}</span> · {t.subject}
                </Link>
                <PriorityBadge priority={t.priority} />
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
        <SearchBar value={search} onChange={setSearch} />
        <StatusFilter value={status} onChange={setStatus} />
      </div>

      <div className="mt-4 rounded-lg border border-slate-200 bg-white">
        {loading && <LoadingState />}
        {!loading && error && <ErrorState message={error} onRetry={retry} />}
        {!loading && !error && tickets.length === 0 && <EmptyState />}
        {!loading && !error && tickets.length > 0 && <TicketTable tickets={tickets} />}
      </div>
    </div>
  )
}
