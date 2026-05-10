const VISITOR_EXPERIENCES = [
  {
    id: 1,
    name: 'Priya Sharma',
    occupation: 'Social Worker',
    place: 'Bhubaneswar',
    avatar: 'woman',
    about: 'Working with communities for over a decade. Visiting Bandhu reinforced my belief in dignity-based development.',
    quote: 'Visiting Bandhu was a deeply moving experience. The warmth and dedication of everyone here reminded me what community truly means. I left with a renewed sense of hope.',
    facebookUrl: '',
    linkedinUrl: 'https://linkedin.com/in/example',
  },
  {
    id: 2,
    name: 'Dr. Rajesh Mohanty',
    occupation: 'Educationist',
    place: 'Cuttack',
    avatar: 'man',
    about: 'Faculty in education. Inspired by Bandhu\'s approach to nurturing values and self-worth among youth.',
    quote: 'I came to understand Bandhu\'s work in villages and cities. The focus on dignity and self-worth, rather than charity, is what makes this organisation special. Truly inspiring.',
    facebookUrl: '',
    linkedinUrl: '',
  },
  {
    id: 3,
    name: 'Anita Das',
    occupation: 'Community Volunteer',
    place: 'Puri',
    avatar: 'woman',
    about: 'Volunteer and advocate for rural development. My day at Bandhughar was a reminder of what partnership can achieve.',
    quote: 'Spent a day at Bandhughar and saw how they support people as equal partners. The environment is peaceful and purposeful. I recommend anyone to visit and see for themselves.',
    facebookUrl: 'https://facebook.com/example',
    linkedinUrl: '',
  },
  {
    id: 4,
    name: 'Suresh Patnaik',
    occupation: 'Development Consultant',
    place: 'Berhampur',
    avatar: 'man',
    about: 'Consultant in development sector. Grateful to have met the team and heard stories from the ground.',
    quote: 'Bandhu doesn\'t just talk about change—they live it. Meeting the team and hearing stories from the ground was humbling. Grateful to have shared this experience.',
    facebookUrl: '',
    linkedinUrl: '',
  },
]

import { useState, useMemo, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'

const CARDS_PER_VIEW = 2
const AUTO_INTERVAL_MS = 5000

function chunkVisitors(list, size) {
  const out = []
  for (let i = 0; i < list.length; i += size) {
    out.push(list.slice(i, i + size))
  }
  return out
}

// Profile pic from img folder: man.png or woman.png
function avatarUrl(visitor) {
  const gender = visitor?.avatar === 'woman' ? 'woman' : 'man'
  return `/static/img/${gender}.png`
}

/** Plain white cards, subtle border. Hover = light grey tint (no translateY — clips under overflow-hidden). */
function VisitorCard({ visitor, onOpen }) {
  return (
    <div
      className="visitor-card min-w-0 rounded-2xl overflow-hidden p-6 sm:p-8 flex flex-col relative border border-slate-200/90 bg-slate-100/95 shadow-none transition-colors duration-200 cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-slate-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-100 hover:border-slate-300 hover:bg-slate-200/40 active:bg-slate-200/50"
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
          <img
            src={avatarUrl(visitor)}
            alt={visitor.name}
            className="w-14 h-14 sm:w-16 sm:h-16 rounded-full object-cover shrink-0 ring-2 ring-slate-200"
          />
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

export default function OurVisitors() {
  const [selected, setSelected] = useState(null)
  const [page, setPage] = useState(0)
  const [paused, setPaused] = useState(false)

  const pages = useMemo(() => chunkVisitors(VISITOR_EXPERIENCES, CARDS_PER_VIEW), [])
  const pageCount = pages.length
  const slidePercent = pageCount > 0 ? 100 / pageCount : 100

  const goNext = useCallback(() => {
    setPage((p) => (p + 1) % pageCount)
  }, [pageCount])

  useEffect(() => {
    if (pageCount <= 1 || paused) return undefined
    const id = window.setInterval(goNext, AUTO_INTERVAL_MS)
    return () => window.clearInterval(id)
  }, [pageCount, paused, goNext])

  return (
    <section
      id="our-visitors"
      className="landing-section bg-white -mt-4 sm:-mt-5 md:-mt-6"
      style={{ backgroundColor: '#ffffff' }}
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6" style={{ backgroundColor: '#ffffff' }}>
        <h2 className="section-title text-center mb-4">Our Visitors</h2>
        <p className="font-body text-slate-600 text-center max-w-2xl mx-auto mb-10 text-lg font-medium">
          People who visited Bandhu share their experience.
        </p>

        {/* overflow-hidden: horizontal slide only. Card hover must not use translateY (was clipping top). */}
        <div
          className="relative w-full overflow-hidden rounded-2xl bg-white"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
          role="region"
          aria-roledescription="carousel"
          aria-label="Visitor testimonials"
        >
          <div
            className="flex flex-nowrap motion-reduce:transition-none bg-white"
            style={{
              width: `${pageCount * 100}%`,
              transform: `translate3d(-${page * slidePercent}%, 0, 0)`,
              transition: 'transform 500ms ease-in-out',
            }}
          >
            {pages.map((pair, pageIndex) => (
              <div
                key={pageIndex}
                className="grid grid-cols-2 gap-3 sm:gap-6 box-border bg-white"
                style={{
                  flex: `0 0 ${slidePercent}%`,
                  width: `${slidePercent}%`,
                  minWidth: `${slidePercent}%`,
                  maxWidth: `${slidePercent}%`,
                }}
              >
                {pair.map((visitor) => (
                  <VisitorCard key={visitor.id} visitor={visitor} onOpen={setSelected} />
                ))}
              </div>
            ))}
          </div>
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

      {/* Portal to document.body — modal was inside #our-visitors; later .landing-section siblings stacked above and hid the dimmer from About downward. */}
      {selected &&
        createPortal(
          <>
            <style>{`
            .visitor-profile-modal-wrap { width: 90vw !important; max-width: 56rem !important; }
            .visitor-profile-modal-close { position: absolute !important; top: 0.75rem !important; right: 1rem !important; z-index: 30 !important; }
          `}</style>
            <div
              className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50"
              onClick={() => setSelected(null)}
              role="dialog"
              aria-modal="true"
              aria-labelledby="visitor-modal-title"
            >
            <div
              className="visitor-profile-modal visitor-profile-modal-wrap bg-white rounded-2xl w-full overflow-hidden flex flex-col sm:flex-row relative border border-slate-200"
              style={{ width: '90vw', maxWidth: '56rem', boxShadow: '0 24px 48px rgba(15, 23, 42, 0.12)' }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button: top-right of modal */}
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
              <img
                src={avatarUrl(selected)}
                alt={selected.name}
                className="relative z-10 w-28 h-28 sm:w-32 sm:h-32 rounded-full object-cover border-4 border-white ring-2 ring-slate-200"
              />
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
