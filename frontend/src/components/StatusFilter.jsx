const OPTIONS = ['All', 'Open', 'In Progress', 'Closed']

export default function StatusFilter({ value, onChange }) {
  return (
    <div role="group" aria-label="Filter by status" className="flex flex-wrap gap-1 rounded-md border border-slate-200 bg-white p-1">
      {OPTIONS.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => onChange(option)}
          aria-pressed={value === option}
          className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
            value === option ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  )
}
