import { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import { createPortal } from 'react-dom'

export default function Gallery({ data }) {
  const photos = useMemo(() => {
    const seen = new Set()
    return (data?.photos || []).filter((photo) => {
      if (!photo?.picture || seen.has(photo.picture)) return false
      seen.add(photo.picture)
      return true
    })
  }, [data?.photos])
  const tagline = data?.gallery_tagline || 'Moments from our journey.'
  const [filter, setFilter] = useState('all')
  const [lightboxIndex, setLightboxIndex] = useState(null)
  const scrollRef = useRef(null)

  const normalizeTagKey = (tag) => {
    if (!tag || typeof tag !== 'string') return null
    return tag
      .trim()
      .replace(/[^\p{L}\p{N}\s]/gu, '') // remove commas/quotes/etc
      .replace(/\s+/g, ' ')
      .toLowerCase()
  }

  const titleCase = (s) => {
    if (!s) return ''
    return s
      .trim()
      .split(/\s+/g)
      .map((w) => (w ? `${w[0].toUpperCase()}${w.slice(1)}` : w))
      .join(' ')
  }

  // If admin stored tagline in ALL CAPS, convert to sentence case for readability.
  const normalizeTagline = (t) => {
    if (!t || typeof t !== 'string') return ''
    const trimmed = t.trim()
    const hasLetters = /[a-zA-Z]/.test(trimmed)
    const looksAllCaps = hasLetters && trimmed === trimmed.toUpperCase()
    if (!looksAllCaps) return trimmed

    const lower = trimmed.toLowerCase()
    // Capitalize first letter of sentence-like segments.
    return lower.replace(/(^\s*[a-z])|([.!?]\s*[a-z])/g, (m) => m.toUpperCase())
  }

  const displayTagline = normalizeTagline(tagline)

  /** One line for masthead blurb: strip DB line breaks and keep "social cause" on the first line. */
  const displayTaglineOneLine = (() => {
    const line = String(displayTagline || '')
      .replace(/[\r\n]+/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
    return line.replace(/ a social/gi, ' a\u00a0social')
  })()

  const normalizeTagsFromPhoto = (p) => (p.tags || []).map(normalizeTagKey).filter(Boolean)

  // Merge duplicate tags caused by case/punctuation differences (e.g. "ankurayan" vs "Ankurayan", "other," etc).
  const tagKeySet = new Set(photos.flatMap((p) => normalizeTagsFromPhoto(p)))

  // Force a consistent, appealing order for filter buttons.
  // (Matches the labels you asked for: Ankurayan, Anandakendra, Bandhughar, Activities, Other)
  const preferredOrder = ['ankurayan', 'anandakendra', 'bandhughar', 'activities', 'other']
  const orderedPreferred = preferredOrder.filter((k) => tagKeySet.has(k))
  const remaining = Array.from(tagKeySet).filter((k) => !preferredOrder.includes(k)).sort()

  const tags = ['all', ...orderedPreferred, ...remaining]

  const filtered =
    filter === 'all' ? photos : photos.filter((p) => normalizeTagsFromPhoto(p).includes(filter))

  const openLightbox = useCallback((index) => setLightboxIndex(index), [])
  const closeLightbox = useCallback(() => setLightboxIndex(null), [])

  useEffect(() => {
    if (lightboxIndex == null) return
    const onKey = (e) => {
      if (e.key === 'Escape') closeLightbox()
      if (e.key === 'ArrowLeft') setLightboxIndex((i) => (i <= 0 ? filtered.length - 1 : i - 1))
      if (e.key === 'ArrowRight') setLightboxIndex((i) => (i >= filtered.length - 1 ? 0 : i + 1))
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [lightboxIndex, filtered.length, closeLightbox])

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollLeft = 0
  }, [filter])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return undefined

    const cards = el.querySelectorAll('[data-gallery-card]')
    if (cards.length <= 1) return undefined

    let paused = false
    const pause = () => { paused = true }
    const resume = () => { paused = false }

    el.addEventListener('mouseenter', pause)
    el.addEventListener('mouseleave', resume)
    el.addEventListener('focusin', pause)
    el.addEventListener('focusout', resume)

    const intervalId = window.setInterval(() => {
      if (paused) return
      const maxScroll = el.scrollWidth - el.clientWidth
      if (maxScroll <= 0) return
      const card = el.querySelector('[data-gallery-card]')
      const row = el.firstElementChild
      const gap = row
        ? parseFloat(window.getComputedStyle(row).columnGap || window.getComputedStyle(row).gap || '32')
        : 32
      const step = card ? card.offsetWidth + (Number.isFinite(gap) ? gap : 32) : 412
      el.scrollLeft += step
      if (el.scrollLeft >= maxScroll - 2) el.scrollLeft = 0
    }, 3000)

    return () => {
      window.clearInterval(intervalId)
      el.removeEventListener('mouseenter', pause)
      el.removeEventListener('mouseleave', resume)
      el.removeEventListener('focusin', pause)
      el.removeEventListener('focusout', resume)
    }
  }, [filtered])

  const current = lightboxIndex != null ? filtered[lightboxIndex] : null

  return (
    <section id="gallery" className="landing-section bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="mb-8 flex flex-col items-center gap-6">
          <h2 className="section-title text-center">Gallery</h2>
          <p className="font-body text-slate-700 text-center font-medium w-full px-2 text-[clamp(0.95rem,1.1vw,1.2rem)] leading-snug md:whitespace-nowrap max-md:max-w-xl max-md:mx-auto">
            {displayTaglineOneLine}
          </p>
          {tags.length > 1 && (
            <div className="w-full max-w-full -mx-4 px-4 sm:mx-0 sm:px-0">
              <div
                className="flex flex-nowrap items-center justify-start gap-x-0 overflow-x-auto scrollbar-hide scroll-smooth sm:justify-center sm:overflow-visible"
                role="tablist"
                aria-label="Gallery categories"
              >
                {tags.map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    role="tab"
                    aria-selected={filter === tag}
                    onClick={() => setFilter(tag)}
                    className={`shrink-0 px-3 sm:px-4 py-2.5 transition-colors duration-200 bg-transparent rounded-none outline-none shadow-none border-0 border-b-2 whitespace-nowrap touch-manipulation text-[0.72rem] font-bold tracking-[0.1em] uppercase ${
                      filter === tag
                        ? 'border-b-[#005E66] text-[#0b3540]'
                        : 'border-b-transparent text-slate-700 hover:text-slate-900'
                    }`}
                  >
                    {tag === 'all' ? 'All' : titleCase(tag)}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div
          ref={scrollRef}
          data-gallery-scroll
          className="gallery-scroll-track overflow-x-auto overflow-y-hidden scrollbar-hide scroll-smooth snap-x snap-mandatory mx-auto w-full max-w-full rounded-2xl py-2 sm:w-[1180px]"
        >
          <div className="flex w-full sm:w-max min-w-full box-border gap-0 sm:gap-8 px-0 sm:px-4">
            {filtered.map((photo, i) => (
              <button
                key={photo.picture || String(i)}
                type="button"
                data-gallery-card
                onClick={() => openLightbox(i)}
                className="gallery-card-shell flex-shrink-0 w-full min-w-full snap-center sm:min-w-0 sm:w-[380px] sm:snap-start aspect-square rounded-2xl overflow-hidden bg-white group shadow-[var(--card-shadow)] border border-teal/20 hover:shadow-[var(--card-shadow-hover)] transition-shadow duration-300 p-0 text-left cursor-pointer block"
              >
                <img
                  src={photo.picture}
                  alt={photo.caption || 'Gallery'}
                  className="w-full h-full object-cover group-hover:scale-105 transition duration-500"
                />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Full-view lightbox: render in portal so it appears above navbar (z-[9999]) */}
      {current && createPortal(
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Image full view"
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90"
          onClick={closeLightbox}
        >
          <button
            type="button"
            onClick={closeLightbox}
            className="absolute top-4 right-4 z-10 w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 text-white flex items-center justify-center text-3xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
          {filtered.length > 1 && (
            <>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setLightboxIndex((i) => (i <= 0 ? filtered.length - 1 : i - 1)) }}
                className="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-14 h-14 rounded-full bg-white/20 hover:bg-white/30 text-white flex items-center justify-center text-4xl"
                aria-label="Previous image"
              >
                ‹
              </button>
              <button
                type="button"
                onClick={(e) => { e.stopPropagation(); setLightboxIndex((i) => (i >= filtered.length - 1 ? 0 : i + 1)) }}
                className="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-14 h-14 rounded-full bg-white/20 hover:bg-white/30 text-white flex items-center justify-center text-4xl"
                aria-label="Next image"
              >
                ›
              </button>
            </>
          )}
          <div
            className="max-w-[90vw] max-h-[90vh] flex items-center justify-center p-4"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={current.picture}
              alt={current.caption || 'Gallery'}
              className="max-h-[90vh] w-auto max-w-full object-contain rounded-2xl shadow-2xl"
            />
          </div>
          {current.caption && (
            <p className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/90 text-center text-sm max-w-[90vw] px-4">
              {current.caption}
            </p>
          )}
        </div>,
        document.body
      )}
    </section>
  )
}
