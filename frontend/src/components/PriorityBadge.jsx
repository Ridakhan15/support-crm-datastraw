const STYLES = {
  Low: 'bg-slate-50 text-slate-600 ring-slate-500/20',
  Medium: 'bg-brand-50 text-brand-700 ring-brand-600/20',
  High: 'bg-rose-50 text-rose-700 ring-rose-600/20',
}

export default function PriorityBadge({ priority }) {
  const style = STYLES[priority] || STYLES.Medium
  return (
    <span className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${style}`}>
      {priority}
    </span>
  )
}
