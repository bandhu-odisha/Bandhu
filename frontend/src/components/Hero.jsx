import { useState, useEffect } from 'react'

const HERO_SLIDE_MS = 6000

/** Single-slide safety net — rendered only if the DB has no active hero slides. */
const HERO_FALLBACK_SLIDES = [
  { image: '/static/img/our_mission.jpg', title: 'Bandhu', subtitle: '' },
]

export default function Hero({ data }) {
  const [index, setIndex] = useState(0)
  const logoUrl = data?.logo_url || null
  const slides = data?.hero_slides?.length ? data.hero_slides : HERO_FALLBACK_SLIDES

  useEffect(() => {
    if (slides.length <= 1) return undefined
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % slides.length)
    }, HERO_SLIDE_MS)
    return () => window.clearInterval(id)
  }, [slides.length])

  const slide = slides[index]

  return (
    <section
      id="top"
      className="relative overflow-hidden bg-white"
      aria-roledescription="carousel"
      aria-label="Bandhu highlights"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 lg:py-16">
        <div className="grid grid-cols-1 justify-items-center gap-10 lg:grid-cols-2 lg:justify-items-stretch lg:gap-12 xl:gap-16 lg:items-stretch">
          {/* Image first on mobile; centered in the column */}
          <div className="order-1 flex w-full max-w-lg flex-col items-center justify-self-center lg:order-2 lg:max-w-none lg:justify-self-auto">
            <div className="relative w-full rounded-2xl overflow-hidden bg-slate-100 aspect-[4/3] shadow-[0_10px_28px_rgba(15,23,42,0.12)]">
              {slides.map((s, i) =>
                s.image ? (
                  <img
                    key={`${s.image}-${String(i)}`}
                    src={s.image}
                    alt=""
                    className={`absolute inset-0 h-full w-full object-cover object-center transition-opacity duration-700 ease-out ${
                      i === index ? 'opacity-100 z-[1]' : 'opacity-0 z-0'
                    }`}
                    loading={i === 0 ? 'eager' : 'lazy'}
                    decoding="async"
                  />
                ) : null
              )}
            </div>
            <div
              className="mt-4 flex w-full justify-center lg:hidden"
              role="tablist"
              aria-label="Hero slides"
            >
              <div className="flex items-center justify-center gap-2">
                {slides.map((_, i) => (
                  <button
                    key={`mobile-dot-${String(i)}`}
                    type="button"
                    role="tab"
                    aria-selected={i === index}
                    aria-label={`Slide ${i + 1}`}
                    className={`h-2.5 rounded-full transition-all duration-300 ${
                      i === index
                        ? 'w-8 bg-[#005E66] shadow-sm'
                        : 'w-2.5 bg-slate-300 hover:bg-slate-400'
                    }`}
                    onClick={() => setIndex(i)}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="order-2 flex min-h-0 w-full max-w-lg flex-col max-lg:items-center max-lg:text-center lg:order-1 lg:max-w-none lg:items-start lg:text-left lg:h-full">
            <div className="flex min-h-0 w-full flex-1 flex-col max-lg:items-center lg:items-start lg:justify-center lg:py-2">
              <div className="mb-7 flex w-full items-center gap-4 max-lg:justify-center sm:mb-8 sm:gap-6 lg:justify-start">
                {logoUrl ? (
                  <img
                    src={logoUrl}
                    alt="Bandhu logo"
                    className="h-24 w-24 shrink-0 object-contain sm:h-28 sm:w-28"
                    width={112}
                    height={112}
                    style={{ maxWidth: 112, maxHeight: 112 }}
                  />
                ) : (
                  <div
                    className="h-24 w-24 shrink-0 rounded-full bg-slate-100 sm:h-28 sm:w-28"
                    aria-hidden
                  />
                )}
                <h2 className="font-sans text-4xl font-black leading-[0.92] tracking-[-0.03em] text-[#004f57] sm:text-5xl md:text-6xl lg:text-[4.35rem] xl:text-[4.85rem]">
                  Bandhu
                </h2>
              </div>
              <h1 className="mb-4 w-full font-sans text-xl font-bold leading-tight tracking-tight text-slate-900 max-lg:text-center sm:mb-5 sm:text-2xl md:text-3xl lg:text-left lg:text-[clamp(1.625rem,0.35rem+2.35vw,2.125rem)] xl:text-[clamp(1.75rem,0.5rem+2.1vw,2.35rem)]">
                {slide.title}
              </h1>
              <p className="w-full max-w-xl max-lg:mx-auto max-lg:text-center font-sans text-[0.9375rem] leading-relaxed text-slate-700 sm:text-base md:text-lg lg:mx-0 lg:text-left">
                {slide.subtitle}
              </p>
            </div>
            <div className="mt-10 hidden w-full justify-start lg:flex lg:mt-0 lg:pt-4">
              <div
                className="flex items-center justify-center gap-2"
                role="tablist"
                aria-label="Hero slides"
              >
                {slides.map((_, i) => (
                  <button
                    key={`desktop-dot-${String(i)}`}
                    type="button"
                    role="tab"
                    aria-selected={i === index}
                    aria-label={`Slide ${i + 1}`}
                    className={`h-2.5 rounded-full transition-all duration-300 ${
                      i === index
                        ? 'w-8 bg-[#005E66] shadow-sm'
                        : 'w-2.5 bg-slate-300 hover:bg-slate-400'
                    }`}
                    onClick={() => setIndex(i)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
