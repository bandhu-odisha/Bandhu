import { useState, useEffect, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { CTA_PILL_CLASS } from '../cta'

function stripHtml(html) {
  if (!html || typeof html !== 'string') return ''
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function normalizeUrl(url) {
  if (!url || typeof url !== 'string') return null
  const u = url.trim()
  if (!u || u === '#') return null
  return u
}

function buildItems(data) {
  const updates = data?.current_updates || []
  const activities = data?.recent_activities || []

  let items = []
  if (updates.length) {
    items = updates
      .map((u) => {
        const text = stripHtml(u.desc)
        if (!text) return null
        return { text, url: normalizeUrl(u.url) }
      })
      .filter(Boolean)
  }
  if (!items.length && activities.length) {
    items = activities
      .map((a) => {
        const title = (a.title || '').trim()
        const desc = stripHtml(a.description || '')
        const line = title ? (desc ? `${title}: ${desc}` : title) : desc
        if (!line) return null
        return { text: line, url: normalizeUrl(a.link) }
      })
      .filter(Boolean)
  }
  if (!items.length) {
    items = [{ text: 'Welcome to Bandhu Odisha — check back for updates.', url: null }]
  }
  return items
}

/**
 * Floating “Current updates” control: opens a vertical notice-board-style panel (slide-over).
 */
export default function CurrentUpdates({ data, inline = false }) {
  const items = useMemo(() => buildItems(data), [data])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (!open) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [open])

  const panel =
    open &&
    typeof document !== 'undefined' &&
    createPortal(
      <div className="fixed inset-0 z-[180]" role="dialog" aria-modal="true" aria-labelledby="current-updates-title">
        <button
          type="button"
          className="absolute inset-0 bg-slate-900/40 backdrop-blur-[1px]"
          aria-label="Close updates"
          onClick={() => setOpen(false)}
        />
        <aside className="absolute top-0 right-0 flex h-full w-full max-w-md flex-col bg-white shadow-[-12px_0_40px_rgba(15,23,42,0.12)] animate-[bandhu-slide-in_0.25s_ease-out]">
          <div className="flex shrink-0 items-center justify-between gap-3 bg-[#005E66] px-4 py-3.5 text-white">
            <div className="min-w-0">
              <h2 id="current-updates-title" className="font-heading text-lg font-bold tracking-tight">
                Current updates
              </h2>
              <p className="mt-0.5 font-body text-xs text-white/85">Notice board</p>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/25 bg-white/10 text-white transition-colors hover:bg-white/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60"
              aria-label="Close"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <ul className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
            {items.map((item, i) => (
              <li key={i} className="border-b border-slate-100 last:border-0">
                {item.url ? (
                  <a
                    href={item.url}
                    className="group block px-4 py-3.5 text-left transition-colors hover:bg-[#f4f6f7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#005E66]/30"
                    target={/^https?:\/\//i.test(item.url) ? '_blank' : undefined}
                    rel={/^https?:\/\//i.test(item.url) ? 'noopener noreferrer' : undefined}
                    onClick={() => setOpen(false)}
                  >
                    <p className="font-body text-sm leading-relaxed text-slate-700">{item.text}</p>
                    <span className="mt-2 inline-block font-body text-xs font-semibold text-[#005E66] opacity-90 group-hover:underline">
                      Open link →
                    </span>
                  </a>
                ) : (
                  <div className="px-4 py-3.5">
                    <p className="font-body text-sm leading-relaxed text-slate-700">{item.text}</p>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </aside>
        <style>{`
          @keyframes bandhu-slide-in {
            from { transform: translateX(100%); }
            to { transform: translateX(0); }
          }
        `}</style>
      </div>,
      document.body
    )

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-expanded={open}
        aria-haspopup="dialog"
        className={
          inline
            ? `${CTA_PILL_CLASS} gap-2 px-3.5 sm:px-4 py-2 sm:py-2.5 whitespace-nowrap`
            : `fixed bottom-5 right-5 z-[170] max-w-[calc(100vw-2.5rem)] gap-2 pl-4 shadow-[0_10px_30px_rgba(0,94,102,0.35)] transition-transform hover:scale-[1.02] sm:bottom-7 sm:right-7 ${CTA_PILL_CLASS}`
        }
        style={inline ? undefined : { marginBottom: 'max(0.25rem, env(safe-area-inset-bottom, 0px))' }}
      >
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white/20">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-4v14c-1.543-2.766-5.067-4-9.168-4H7a3.988 3.988 0 01-1.564-.317z"
            />
          </svg>
        </span>
        <span>Updates</span>
      </button>
      {panel}
    </>
  )
}
