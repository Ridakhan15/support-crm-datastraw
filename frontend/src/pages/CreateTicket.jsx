import { useState } from 'react'
import { CheckCircle2 } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../services/api.js'
import { useToast } from '../components/Toast.jsx'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const EMPTY_FORM = { customer_name: '', customer_email: '', subject: '', description: '', priority: 'Medium' }

/** Client-side validation mirrors the backend's rules so users see errors instantly,
 * but the backend is the source of truth — see the catch block in handleSubmit. */
function validate(form) {
  const errors = {}
  if (!form.customer_name.trim()) errors.customer_name = 'Customer name is required.'
  if (!form.customer_email.trim()) errors.customer_email = 'Customer email is required.'
  else if (!EMAIL_RE.test(form.customer_email.trim())) errors.customer_email = 'Enter a valid email address.'
  if (!form.subject.trim()) errors.subject = 'Subject is required.'
  if (!form.description.trim()) errors.description = 'Description is required.'
  return errors
}

export default function CreateTicket() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [created, setCreated] = useState(null) // { ticket_id } once creation succeeds

  const setField = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  async function handleSubmit(e) {
    e.preventDefault()
    const clientErrors = validate(form)
    setErrors(clientErrors)
    if (Object.keys(clientErrors).length > 0) return

    setSubmitting(true)
    try {
      const result = await api.createTicket(form)
      setCreated(result)
      showToast(`Ticket ${result.ticket_id} created successfully.`)
    } catch (err) {
      // Server-side validation is the final authority (e.g. a race, or a rule the client missed).
      const message = err instanceof ApiError ? err.message : 'Failed to create ticket. Please try again.'
      showToast(message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  if (created) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center sm:px-6">
        <CheckCircle2 className="mx-auto h-10 w-10 text-emerald-500" aria-hidden="true" />
        <h1 className="mt-4 text-xl font-semibold text-slate-900">
          Ticket {created.ticket_id} created successfully.
        </h1>
        <p className="mt-1 text-sm text-slate-500">The customer's request has been logged.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to={`/tickets/${created.ticket_id}`} className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
            View Ticket
          </Link>
          <Link to="/" className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8 sm:px-6">
      <nav aria-label="Breadcrumb" className="mb-2 text-sm text-slate-500">
        <Link to="/" className="hover:underline">Dashboard</Link>
        <span className="mx-1.5">/</span>
        <span className="text-slate-700">New Ticket</span>
      </nav>
      <h1 className="text-2xl font-semibold text-slate-900">New Ticket</h1>

      <form onSubmit={handleSubmit} noValidate className="mt-6 space-y-5">
        <Field label="Customer Name" required error={errors.customer_name}>
          <input
            type="text"
            value={form.customer_name}
            onChange={setField('customer_name')}
            className={inputClass(errors.customer_name)}
          />
        </Field>

        <Field label="Customer Email" required error={errors.customer_email}>
          <input
            type="email"
            value={form.customer_email}
            onChange={setField('customer_email')}
            className={inputClass(errors.customer_email)}
          />
        </Field>

        <Field label="Subject" required error={errors.subject}>
          <input
            type="text"
            value={form.subject}
            onChange={setField('subject')}
            className={inputClass(errors.subject)}
          />
        </Field>

        <Field label="Description" required error={errors.description}>
          <textarea
            rows={5}
            value={form.description}
            onChange={setField('description')}
            className={inputClass(errors.description)}
          />
        </Field>

        <Field label="Priority">
          <select value={form.priority} onChange={setField('priority')} className={inputClass()}>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </Field>

        <button
          type="submit"
          disabled={submitting}
          className="inline-flex w-full items-center justify-center rounded-md bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create Ticket'}
        </button>
      </form>
    </div>
  )
}

function Field({ label, required, error, children }) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-slate-700">
        {label} {required && <span className="text-rose-500">*</span>}
      </label>
      {children}
      {error && <p className="mt-1 text-sm text-rose-600">{error}</p>}
    </div>
  )
}

function inputClass(error) {
  return `w-full rounded-md border px-3 py-2 text-sm text-slate-900 focus-visible:outline-none ${
    error ? 'border-rose-400' : 'border-slate-300 focus-visible:border-brand-500'
  }`
}
