import { Inbox } from 'lucide-react'

export default function EmptyState({ title = 'No tickets found', message = 'Try changing your search or filters.' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
      <Inbox className="h-8 w-8 text-slate-300" aria-hidden="true" />
      <p className="font-medium text-slate-700">{title}</p>
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  )
}
