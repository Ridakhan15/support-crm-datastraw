import { LifeBuoy, Plus } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()
  const onCreatePage = location.pathname === '/tickets/new'

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2 text-slate-900">
          <LifeBuoy className="h-5 w-5 text-brand-600" aria-hidden="true" />
          <span className="font-semibold">Support CRM</span>
        </Link>

        {!onCreatePage && (
          <Link
            to="/tickets/new"
            className="inline-flex items-center gap-1.5 rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 focus-visible:outline-none"
          >
            <Plus className="h-4 w-4" aria-hidden="true" />
            New Ticket
          </Link>
        )}
      </div>
    </header>
  )
}
