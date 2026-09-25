import { useNavigate } from 'react-router-dom'
import StatusBadge from './StatusBadge.jsx'
import PriorityBadge from './PriorityBadge.jsx'

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

export default function TicketTable({ tickets }) {
  const navigate = useNavigate()
  const goToTicket = (ticketId) => navigate(`/tickets/${ticketId}`)

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-slate-500">
            <th scope="col" className="px-4 py-3 font-medium">Ticket ID</th>
            <th scope="col" className="px-4 py-3 font-medium">Customer</th>
            <th scope="col" className="px-4 py-3 font-medium">Subject</th>
            <th scope="col" className="px-4 py-3 font-medium">Priority</th>
            <th scope="col" className="px-4 py-3 font-medium">Status</th>
            <th scope="col" className="px-4 py-3 font-medium">Created</th>
            <th scope="col" className="px-4 py-3 font-medium">
              <span className="sr-only">Action</span>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {tickets.map((ticket) => (
            <tr
              key={ticket.ticket_id}
              onClick={() => goToTicket(ticket.ticket_id)}
              onKeyDown={(e) => e.key === 'Enter' && goToTicket(ticket.ticket_id)}
              tabIndex={0}
              role="button"
              aria-label={`Open ticket ${ticket.ticket_id}`}
              className="cursor-pointer hover:bg-slate-50 focus-visible:bg-slate-50"
            >
              <td className="px-4 py-3 font-medium text-slate-900">{ticket.ticket_id}</td>
              <td className="px-4 py-3 text-slate-700">{ticket.customer_name}</td>
              <td className="px-4 py-3 text-slate-700">{ticket.subject}</td>
              <td className="px-4 py-3"><PriorityBadge priority={ticket.priority} /></td>
              <td className="px-4 py-3"><StatusBadge status={ticket.status} /></td>
              <td className="px-4 py-3 text-slate-500">{formatDate(ticket.created_at)}</td>
              <td className="px-4 py-3 text-brand-600">View</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
