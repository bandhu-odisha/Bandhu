import { useCallback, useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { CTA_PILL_CLASS } from '../cta'

const TEAL = '#005E66'

const emptyForm = {
  report_id: '',
  year: '',
  title: '',
  external_url: '',
  is_published: true,
}

function getCsrfToken(explicit) {
  if (explicit) return explicit
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

export default function AnnualReportUploadModal({ open, onClose, uploadUrl, csrfToken }) {
  const panelRef = useRef(null)
  const fileRef = useRef(null)
  const [form, setForm] = useState(emptyForm)
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)
  const [errors, setErrors] = useState({})

  const resetForm = useCallback(() => {
    setForm(emptyForm)
    setErrors({})
    if (fileRef.current) fileRef.current.value = ''
  }, [])

  const loadReports = useCallback(async () => {
    if (!uploadUrl) return
    setLoading(true)
    setMessage(null)
    try {
      const res = await fetch(`${uploadUrl}?format=json`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'application/json' },
        credentials: 'same-origin',
      })
      if (!res.ok) throw new Error('Could not load reports')
      const data = await res.json()
      setReports(data.reports || [])
    } catch {
      setMessage({ type: 'error', text: 'Could not load reports. Please refresh the page.' })
    } finally {
      setLoading(false)
    }
  }, [uploadUrl])

  useEffect(() => {
    if (!open) return
    resetForm()
    loadReports()
  }, [open, loadReports, resetForm])

  useEffect(() => {
    if (!open) return
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  const startEdit = (report) => {
    setForm({
      report_id: String(report.id),
      year: String(report.year),
      title: report.title || '',
      external_url: report.external_url || '',
      is_published: report.is_published,
    })
    setErrors({})
    setMessage(null)
    if (fileRef.current) fileRef.current.value = ''
    panelRef.current?.querySelector('#annual-report-year')?.focus()
  }

  const handleDelete = async (report) => {
    if (!window.confirm(`Delete ${report.title}?`)) return
    setSaving(true)
    setMessage(null)
    try {
      const body = new FormData()
      body.append('csrfmiddlewaretoken', getCsrfToken(csrfToken))
      body.append('action', 'delete')
      body.append('report_id', String(report.id))
      const res = await fetch(uploadUrl, {
        method: 'POST',
        body,
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
      const data = await res.json()
      if (!res.ok || !data.ok) throw new Error('Delete failed')
      setReports(data.reports || [])
      if (form.report_id === String(report.id)) resetForm()
      setMessage({ type: 'success', text: data.message || 'Deleted.' })
    } catch {
      setMessage({ type: 'error', text: 'Could not delete. Please try again.' })
    } finally {
      setSaving(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setErrors({})
    setMessage(null)
    try {
      const body = new FormData()
      body.append('csrfmiddlewaretoken', getCsrfToken(csrfToken))
      if (form.report_id) body.append('report_id', form.report_id)
      body.append('year', form.year)
      body.append('title', form.title)
      body.append('external_url', form.external_url)
      if (form.is_published) body.append('is_published', 'on')
      const file = fileRef.current?.files?.[0]
      if (file) body.append('pdf_file', file)

      const res = await fetch(uploadUrl, {
        method: 'POST',
        body,
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      })
      const data = await res.json()
      if (!res.ok || !data.ok) {
        if (data.errors) setErrors(data.errors)
        setMessage({ type: 'error', text: 'Please fix the errors below.' })
        return
      }
      setReports(data.reports || [])
      resetForm()
      setMessage({ type: 'success', text: data.message || 'Saved.' })
      window.setTimeout(() => window.location.reload(), 600)
    } catch {
      setMessage({ type: 'error', text: 'Upload failed. Please try again.' })
    } finally {
      setSaving(false)
    }
  }

  if (!open) return null

  const fieldError = (name) =>
    errors[name]?.length ? (
      <p className="text-xs text-red-600 mt-1" role="alert">
        {errors[name].join(' ')}
      </p>
    ) : null

  return createPortal(
    <div
      className="fixed inset-0 z-[300] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/45 backdrop-blur-[2px]"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div
        ref={panelRef}
        className="relative w-full max-w-lg rounded-t-2xl sm:rounded-2xl bg-white shadow-2xl ring-1 ring-black/10 overflow-hidden max-h-[min(92dvh,720px)] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="annual-report-modal-title"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 sm:px-5 pt-3 sm:pt-4 pb-2 border-b border-black/[0.06] shrink-0">
          <h2 id="annual-report-modal-title" className="font-heading text-base sm:text-lg font-bold text-slate-800">
            Upload annual report
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-4 sm:px-5 py-4 overflow-y-auto flex-1">
          <p className="text-sm text-slate-600 mb-4">
            Add a PDF or Google Drive link for each year. Published reports appear in the footer for visitors.
          </p>

          {message && (
            <p
              className={`text-sm mb-3 px-1 ${message.type === 'success' ? 'text-emerald-700' : 'text-red-600'}`}
              role="alert"
            >
              {message.text}
            </p>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label htmlFor="annual-report-year" className="block text-sm font-medium text-slate-700 mb-1">
                Year
              </label>
              <input
                id="annual-report-year"
                type="number"
                min={2000}
                max={2100}
                required
                value={form.year}
                onChange={(e) => setForm((f) => ({ ...f, year: e.target.value }))}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#005E66]/30 focus:border-[#005E66]"
                placeholder="e.g. 2024"
              />
              {fieldError('year')}
            </div>
            <div>
              <label htmlFor="annual-report-title" className="block text-sm font-medium text-slate-700 mb-1">
                Title (optional)
              </label>
              <input
                id="annual-report-title"
                type="text"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#005E66]/30 focus:border-[#005E66]"
                placeholder="Annual Report 2024"
              />
            </div>
            <div>
              <label htmlFor="annual-report-pdf" className="block text-sm font-medium text-slate-700 mb-1">
                PDF file
              </label>
              <input
                id="annual-report-pdf"
                ref={fileRef}
                type="file"
                accept="application/pdf,.pdf"
                className="w-full text-sm text-slate-600 file:mr-3 file:rounded-full file:border-0 file:bg-[#005E66]/10 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-[#005E66]"
              />
              {fieldError('pdf_file')}
              <p className="text-xs text-slate-500 mt-1">Leave empty if you only use a Drive link.</p>
            </div>
            <div>
              <label htmlFor="annual-report-url" className="block text-sm font-medium text-slate-700 mb-1">
                Google Drive / link
              </label>
              <input
                id="annual-report-url"
                type="url"
                value={form.external_url}
                onChange={(e) => setForm((f) => ({ ...f, external_url: e.target.value }))}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#005E66]/30 focus:border-[#005E66]"
                placeholder="https://drive.google.com/..."
              />
              {fieldError('external_url')}
            </div>
            {errors['__all__']?.length > 0 && (
              <p className="text-xs text-red-600" role="alert">
                {errors['__all__'].join(' ')}
              </p>
            )}
            <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={form.is_published}
                onChange={(e) => setForm((f) => ({ ...f, is_published: e.target.checked }))}
                className="rounded border-slate-300 text-[#005E66] focus:ring-[#005E66]/30"
              />
              Published (show in footer)
            </label>
            <div className="flex flex-wrap gap-2 pt-1">
              <button
                type="submit"
                disabled={saving}
                className={`${CTA_PILL_CLASS} justify-center min-w-[8rem] disabled:opacity-60`}
              >
                {saving ? 'Saving…' : form.report_id ? 'Save changes' : 'Upload report'}
              </button>
              {form.report_id && (
                <button
                  type="button"
                  onClick={resetForm}
                  className="rounded-full px-4 py-2 text-sm font-medium text-slate-600 border border-slate-200 hover:bg-slate-50"
                >
                  Cancel edit
                </button>
              )}
            </div>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100">
            <h3 className="text-sm font-bold text-slate-800 mb-2">Uploaded reports</h3>
            {loading ? (
              <p className="text-sm text-slate-500">Loading…</p>
            ) : reports.length === 0 ? (
              <p className="text-sm text-slate-500">No reports yet.</p>
            ) : (
              <ul className="space-y-2">
                {reports.map((report) => (
                  <li
                    key={report.id}
                    className="flex flex-wrap items-center justify-between gap-2 text-sm border border-slate-100 rounded-lg px-3 py-2"
                  >
                    <span className="text-slate-800">
                      {report.title}{' '}
                      <span className="text-slate-500">({report.year})</span>
                      {!report.is_published && (
                        <span className="text-xs text-amber-700 ml-1">draft</span>
                      )}
                    </span>
                    <span className="flex gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => startEdit(report)}
                        className="font-medium hover:underline"
                        style={{ color: TEAL }}
                      >
                        Edit
                      </button>
                      {report.view_url && (
                        <a
                          href={report.view_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium hover:underline"
                          style={{ color: TEAL }}
                        >
                          View
                        </a>
                      )}
                      <button
                        type="button"
                        onClick={() => handleDelete(report)}
                        disabled={saving}
                        className="text-red-600 font-medium hover:underline disabled:opacity-50"
                      >
                        Delete
                      </button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}
