import { useState, useMemo, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { useMediaQuery } from '../useMediaQuery'

const AUTO_INTERVAL_MS = 5000

function chunkVisitors(list, size) {
  const out = []
  for (let i = 0; i < list.length; i += size) {
    out.push(list.slice(i, i + size))
  }
  return out
}

function avatarUrl(visitor) {
  if (visitor?.photoUrl) return visitor.photoUrl
  const gender = visitor?.avatar === 'woman' ? 'woman' : 'man'
  return `/static/img/${gender}.png`
}

/** Plain white cards, subtle border. Hover = light grey tint (no translateY — clips under overflow-hidden). */
function VisitorCard({ visitor, onOpen }) {
  return (
    <div
      className="visitor-card min-w-0 rounded-2xl overflow-hidden p-6 sm:p-8 flex flex-col relative border border-slate-200/90 bg-slate-100/95 shadow-none transition-colors duration-200 cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-100 hover:border-slate-300 hover:bg-slate-200/40 active:bg-slate-200/50 [&_*]:no-underline"
      onClick={() => onOpen(visitor)}
      onKeyDown={(e) => e.key === 'Enter' && onOpen(visitor)}
      role="button"
      tabIndex={0}
    >
      <div className="relative z-10 flex flex-col flex-1 min-h-0">
        <p className="font-body text-slate-600 text-base sm:text-lg leading-relaxed mb-6 italic">
          &ldquo;{visitor.quote}&rdquo;
        </p>
        <div className="mt-auto border-t border-slate-200 pt-5 flex items-center gap-4">
          <div className="w-14 h-14 sm:w-16 sm:h-16 shrink-0 overflow-hidden rounded-full ring-2 ring-slate-200 bg-slate-200">
            <img
              src={avatarUrl(visitor)}
              alt={visitor.name}
              className="h-full w-full object-cover object-center"
            />
          </div>
          <div className="min-w-0">
            <p className="font-heading font-bold text-slate-900 text-base sm:text-lg">{visitor.name}</p>
            <p className="text-sm text-slate-600 leading-snug">
              {visitor.occupation}, {visitor.place}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function OurVisitors({ data }) {
  const visitors = useMemo(() => data?.visitors || [], [data?.visitors])
  const [selected, setSelected] = useState(null)
  const [page, setPage] = useState(0)
  const [paused, setPaused] = useState(false)
  const isWide = useMediaQuery('(min-width: 640px)', true)
  const cardsPerView = isWide ? (visitors.length === 2 ? 1 : 2) : 1

  const pages = useMemo(
    () => chunkVisitors(visitors, cardsPerView),
    [visitors, cardsPerView]
  )
  const pageCount = pages.length

  useEffect(() => {
    setPage(0)
  }, [visitors.length, cardsPerView])

  useEffect(() => {
    if (pageCount <= 1 || paused) return undefined
    const id = window.setInterval(() => {
      setPage((p) => (p + 1) % pageCount)
    }, AUTO_INTERVAL_MS)
    return () => window.clearInterval(id)
  }, [pageCount, paused])

  if (!visitors.length) {
    return null
  }

  return (
    <section
      id="our-visitors"
      className="landing-section bg-white -mt-4 sm:-mt-5 md:-mt-6"
      style={{ backgroundColor: '#ffffff' }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6" style={{ backgroundColor: '#ffffff' }}>
        <h2 className="section-title text-center mb-4">Our Visitors</h2>
        <p className="landing-section-subtitle">
          People who visited Bandhu share their experience.
        </p>

        <div
          className="relative w-full overflow-hidden rounded-2xl bg-white"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          role="region"
          aria-roledescription="carousel"
          aria-label="Visitor testimonials"
        >
          {pages.map((pair, pageIndex) => (
            <div
              key={pageIndex}
              className={`grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 motion-reduce:transition-none transition-opacity duration-500 ease-in-out ${
                pageIndex === page
                  ? 'relative z-[1] opacity-100'
                  : 'pointer-events-none absolute inset-x-0 top-0 z-0 opacity-0'
              }`}
              aria-hidden={pageIndex !== page}
            >
              {pair.map((visitor) => (
                <VisitorCard
                  key={visitor.id}
                  visitor={visitor}
                  onOpen={setSelected}
                />
              ))}
            </div>
          ))}
        </div>

        {pageCount > 1 && (
          <div className="flex justify-center gap-2 mt-6" role="tablist" aria-label="Testimonial pages">
            {pages.map((_, i) => (
              <button
                key={i}
                type="button"
                role="tab"
                aria-selected={i === page}
                aria-label={`Show testimonials ${i + 1} of ${pageCount}`}
                className={`h-2 rounded-full transition-all duration-300 ${
                  i === page ? 'w-8 bg-slate-500' : 'w-2 bg-slate-300 hover:bg-slate-400'
                }`}
                onClick={() => setPage(i)}
              />
            ))}
          </div>
        )}
      </div>

      {selected &&
        createPortal(
          <>
            <style>{`
            .visitor-profile-modal-wrap { width: min(90vw, calc(100% - 0.75rem)) !important; max-width: 56rem !important; }
            @media (max-width: 639px) {
              .visitor-profile-modal-wrap { width: calc(100% - 0.75rem) !important; max-width: none !important; max-height: min(92dvh, 720px) !important; overflow-y: auto !important; }
            }
            .visitor-profile-modal-close { position: absolute !important; top: 0.75rem !important; right: 1rem !important; z-index: 30 !important; }
          `}</style>
            <div
              className="fixed inset-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/50"
              onClick={() => setSelected(null)}
              role="dialog"
              aria-modal="true"
              aria-labelledby="visitor-modal-title"
            >
              <div
                className="visitor-profile-modal visitor-profile-modal-wrap bg-white rounded-t-2xl sm:rounded-2xl w-full overflow-hidden flex flex-col sm:flex-row relative border border-slate-200"
                style={{ width: '90vw', maxWidth: '56rem', boxShadow: '0 24px 48px rgba(15, 23, 42, 0.12)' }}
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  type="button"
                  className="visitor-profile-modal-close text-2xl leading-none rounded-full flex items-center justify-center border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-slate-700"
                  style={{ width: '2.25rem', height: '2.25rem' }}
                  onClick={() => setSelected(null)}
                  aria-label="Close"
                >
                  &times;
                </button>
                <div className="sm:w-2/5 flex flex-col items-center justify-center p-6 sm:p-8 min-h-[200px] sm:min-h-0 relative overflow-hidden bg-slate-50 border-b sm:border-b-0 sm:border-r border-slate-200">
                  <div className="relative z-10 w-28 h-28 sm:w-32 sm:h-32 overflow-hidden rounded-full border-4 border-white ring-2 ring-slate-200 bg-slate-200">
                    <img
                      src={avatarUrl(selected)}
                      alt={selected.name}
                      className="h-full w-full object-cover object-center"
                    />
                  </div>
                </div>
                <div className="sm:w-3/5 p-6 sm:p-8 bg-white">
                  <h3
                    id="visitor-modal-title"
                    className="font-heading font-bold text-xl sm:text-2xl mb-4 uppercase tracking-wide text-slate-800"
                  >
                    {selected.name}
                  </h3>
                  <dl className="space-y-4 text-sm">
                    <div>
                      <dt className="font-semibold text-xs uppercase tracking-wide mb-1 text-slate-500">About</dt>
                      <dd className="leading-relaxed text-slate-600">{selected.about || '—'}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold text-xs uppercase tracking-wide mb-1 text-slate-500">Profession</dt>
                      <dd className="text-slate-600">{selected.occupation || '—'}</dd>
                    </div>
                    <div>
                      <dt className="font-semibold text-xs uppercase tracking-wide mb-2 text-slate-500">Profile</dt>
                      <dd className="flex flex-wrap items-center gap-2">
                        {selected.facebookUrl ? (
                          <a
                            href={selected.facebookUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-9 h-9 rounded-full flex items-center justify-center border border-slate-200 bg-slate-50 text-slate-400 transition hover:bg-slate-100 hover:border-slate-300 hover:text-slate-600"
                            title="Facebook"
                            aria-label="Facebook"
                          >
                            <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                          </a>
                        ) : (
                          <span
                            className="w-9 h-9 rounded-full flex items-center justify-center border border-slate-100 bg-slate-50 text-slate-400 cursor-default opacity-60"
                            title="Facebook"
                            aria-hidden="true"
                          >
                            <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                          </span>
                        )}
                        {selected.linkedinUrl ? (
                          <a
                            href={selected.linkedinUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="w-9 h-9 rounded-full flex items-center justify-center border border-slate-200 bg-slate-50 text-slate-400 transition hover:bg-slate-100 hover:border-slate-300 hover:text-slate-600"
                            title="LinkedIn"
                            aria-label="LinkedIn"
                          >
                            <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                          </a>
                        ) : (
                          <span
                            className="w-9 h-9 rounded-full flex items-center justify-center border border-slate-100 bg-slate-50 text-slate-400 cursor-default opacity-60"
                            title="LinkedIn"
                            aria-hidden="true"
                          >
                            <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                          </span>
                        )}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </>,
          document.body
        )}
    </section>
  )
}
