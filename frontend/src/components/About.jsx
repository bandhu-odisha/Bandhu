import { useState, useEffect, useMemo, useCallback } from 'react'
import { createPortal } from 'react-dom'

const SLIDE_MS = 5000

/** Split closing sentence so line 5 can be centered on its own on phones. */
function splitAboutDesc(html) {
  if (!html) return { leadHtml: '', closing: null }
  const normalized = String(html).replace(/\u00a0/g, ' ').trim()
  const match = normalized.match(
    /^([\s\S]*?\bBandhu)\s+(does\s+small\s+things\s+with\s+the\s+highest\s+possible\s+sincerity\.?)\s*$/i
  )
  if (!match) return { leadHtml: normalized, closing: null }
  return { leadHtml: match[1], closing: match[2].trim() }
}

const DEFAULT_ABOUT_SLIDES = [
  {
    src: '/static/img/about-slide-1-gardenia.png',
    caption:
      'A gardenia in full bloom—quiet growth, care for the soil, and our bond with the living world.',
  },
  {
    src: '/static/img/about-slide-2-hibiscus.png',
    caption:
      'Double hibiscus in our garden: vivid colour, steady hands, and the joy we find in nurturing life.',
  },
  {
    src: '/static/img/about-slide-3-campus.png',
    caption:
      'Bandhu at twilight—where day’s work meets rest, and our community gathers under an open sky.',
  },
  {
    src: '/static/img/about-slide-4-ixora.png',
    caption:
      'Ixora in bloom: many small flowers, one shared canopy—strength in togetherness.',
  },
  {
    src: '/static/img/about-slide-blossoms.png',
    caption:
      'A full set of blossoms in the green — yellow bells among the vines and leaves, bright in the thicket.',
  },
]

export default function About({ data }) {
  const about = data?.about
  const aboutDescParts = useMemo(() => splitAboutDesc(about?.desc), [about?.desc])
  const slides = useMemo(() => {
    const imported = (data?.about_slides || []).filter((slide) => slide?.src)
    if (imported.length) return imported
    return DEFAULT_ABOUT_SLIDES
  }, [data])
  const [slideIndex, setSlideIndex] = useState(0)
  const [lightboxOpen, setLightboxOpen] = useState(false)

  const openLightbox = useCallback(() => setLightboxOpen(true), [])
  const closeLightbox = useCallback(() => setLightboxOpen(false), [])

  useEffect(() => {
    if (slides.length <= 1) return undefined
    const id = window.setInterval(() => {
      setSlideIndex((i) => (i + 1) % slides.length)
    }, SLIDE_MS)
    return () => window.clearInterval(id)
  }, [slides.length])

  useEffect(() => {
    if (!lightboxOpen) return undefined
    const onKey = (e) => {
      if (e.key === 'Escape') closeLightbox()
      if (e.key === 'ArrowLeft') {
        setSlideIndex((i) => (i <= 0 ? slides.length - 1 : i - 1))
      }
      if (e.key === 'ArrowRight') {
        setSlideIndex((i) => (i >= slides.length - 1 ? 0 : i + 1))
      }
    }
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [lightboxOpen, slides.length, closeLightbox])

  if (!about || !slides.length) return null

  const current = slides[slideIndex]

  return (
    <section id="about" className="landing-section bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <h2 className="section-title text-center mb-8 sm:mb-10">About Us</h2>

        <div className="grid grid-cols-1 justify-items-center gap-6 lg:grid-cols-2 lg:justify-items-stretch lg:gap-8 xl:gap-10 items-stretch">
          <div className="order-2 flex w-full flex-col items-center lg:order-1 lg:items-start lg:-ml-2 xl:-ml-4 2xl:-ml-5">
            <div className="rounded-2xl bg-white w-full py-8 sm:py-12 px-4 sm:px-5 lg:h-full lg:flex lg:flex-col lg:justify-center lg:px-0 lg:pl-0 lg:pr-8 lg:text-left lg:items-start">
              <p
                className="w-full font-body font-bold text-[#0b3540] text-lg sm:text-xl md:text-[1.28rem] lg:text-[1.34rem] leading-snug tracking-tight mb-6 sm:mb-7 max-lg:mx-auto max-lg:max-w-[36rem] max-lg:text-center max-lg:text-balance max-lg:leading-[1.45] lg:text-left [&_a]:text-[#005E66] [&_a]:underline"
                dangerouslySetInnerHTML={{ __html: about.tagline }}
              />
              <div className="about-us-copy w-full max-lg:flex max-lg:flex-col max-lg:items-center">
                <p
                  className="about-us-desc hidden w-full font-body font-normal text-[#3d5c66] text-base sm:text-lg md:text-[1.2rem] lg:text-[1.26rem] lg:block lg:text-left lg:leading-relaxed [&_a]:text-[#005E66] [&_a]:underline"
                  dangerouslySetInnerHTML={{ __html: about.desc }}
                />
                <p
                  className="about-us-desc w-full font-body font-normal text-[#3d5c66] text-base sm:text-lg md:text-[1.2rem] max-lg:max-w-[36rem] max-lg:text-center max-lg:leading-[1.85] lg:hidden [&_a]:text-[#005E66] [&_a]:underline"
                  dangerouslySetInnerHTML={{ __html: aboutDescParts.leadHtml }}
                />
                {aboutDescParts.closing ? (
                  <p className="about-desc-closing m-0 w-full font-body font-normal text-[#3d5c66] max-lg:max-w-[36rem] max-lg:text-center lg:hidden">
                    {aboutDescParts.closing}
                  </p>
                ) : null}
              </div>
            </div>
          </div>

          <div className="order-1 flex w-full max-w-lg flex-col items-center min-h-0 lg:order-2 lg:max-w-none lg:items-stretch lg:h-full">
            <figure className="m-0 flex w-full flex-col flex-1 min-h-0">
              <button
                type="button"
                className="relative w-full aspect-[5/4] sm:aspect-[4/3] min-h-[13rem] lg:aspect-auto lg:flex-1 lg:min-h-[12rem] rounded-2xl overflow-hidden border border-black/[0.08] bg-slate-100 cursor-pointer p-0 text-left"
                aria-live="polite"
                aria-atomic="true"
                aria-label={`View photo: ${current.caption || 'About Bandhu'}`}
                onClick={openLightbox}
              >
                {slides.map((slide, i) => (
                  <img
                    key={`${slide.src}-${String(i)}`}
                    src={slide.src}
                    alt={slide.caption || 'About Bandhu'}
                    className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-out ${
                      i === slideIndex
                        ? 'opacity-100 z-[1] pointer-events-auto'
                        : 'opacity-0 z-0 pointer-events-none'
                    }`}
                    loading={i === 0 ? 'eager' : 'lazy'}
                  />
                ))}
              </button>
              <figcaption className="mt-4 w-full shrink-0 text-center lg:text-left">
                <p className="font-body text-sm sm:text-base text-slate-600 leading-snug min-h-[3rem] sm:min-h-[3.25rem] mx-auto max-w-md lg:mx-0 lg:max-w-none">
                  {slides[slideIndex].caption}
                </p>
                <div
                  className="flex justify-center gap-1.5 mt-3 lg:justify-start"
                  role="tablist"
                  aria-label="Photo carousel position"
                >
                  {slides.map((_, i) => (
                    <button
                      key={String(i)}
                      type="button"
                      role="tab"
                      aria-selected={i === slideIndex}
                      aria-label={`Show photo ${i + 1}`}
                      className={`h-1.5 rounded-full transition-all duration-300 ${
                        i === slideIndex
                          ? 'w-6 bg-[var(--color-teal)]'
                          : 'w-1.5 bg-slate-300 hover:bg-slate-400'
                      }`}
                      onClick={() => setSlideIndex(i)}
                    />
                  ))}
                </div>
              </figcaption>
            </figure>
          </div>
        </div>
      </div>

      {lightboxOpen &&
        current &&
        createPortal(
          <div
            role="dialog"
            aria-modal="true"
            aria-label="About photo full view"
            className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/90"
            onClick={closeLightbox}
          >
            <button
              type="button"
              onClick={closeLightbox}
              className="absolute top-4 right-4 z-10 flex h-12 w-12 items-center justify-center rounded-full bg-white/20 text-3xl leading-none text-white hover:bg-white/30"
              aria-label="Close"
            >
              ×
            </button>
            {slides.length > 1 && (
              <>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSlideIndex((i) => (i <= 0 ? slides.length - 1 : i - 1))
                  }}
                  className="absolute left-4 top-1/2 z-10 flex h-14 w-14 -translate-y-1/2 items-center justify-center rounded-full bg-white/20 text-4xl text-white hover:bg-white/30"
                  aria-label="Previous photo"
                >
                  ‹
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSlideIndex((i) => (i >= slides.length - 1 ? 0 : i + 1))
                  }}
                  className="absolute right-4 top-1/2 z-10 flex h-14 w-14 -translate-y-1/2 items-center justify-center rounded-full bg-white/20 text-4xl text-white hover:bg-white/30"
                  aria-label="Next photo"
                >
                  ›
                </button>
              </>
            )}
            <div
              className="flex max-h-[90vh] max-w-[90vw] items-center justify-center p-4"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={current.src}
                alt={current.caption || 'About Bandhu'}
                className="max-h-[90vh] w-auto max-w-full rounded-2xl object-contain shadow-2xl"
              />
            </div>
            {current.caption && (
              <p className="absolute bottom-4 left-1/2 max-w-[90vw] -translate-x-1/2 px-4 text-center text-sm text-white/90">
                {current.caption}
              </p>
            )}
          </div>,
          document.body
        )}
    </section>
  )
}
