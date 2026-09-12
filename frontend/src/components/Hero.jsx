import { useState, useEffect, useMemo } from 'react'

const HERO_SLIDE_MS = 6000

const HERO_FALLBACK_IMAGES = [
  '/static/img/our_mission.jpg',
  '/static/img/our_mission1.jpg',
  '/static/img/about-slide-3-campus.png',
  '/static/img/about-slide-2-hibiscus.png',
]

const DEFAULT_HERO_SLIDES = [
  {
    title: 'The Friend of the Last Man',
    subtitle:
      'Bandhu is an idea that celebrates goodness — in you, me, and all others. Friendship, sincerity, and small acts that matter.',
  },
  {
    title: 'Goodness in Every Direction',
    subtitle:
      'We are people who care about what is inconsistent within and without — and who choose to do small things with the highest sincerity.',
  },
  {
    title: 'Bandhu at twilight',
    subtitle:
      'The campus quiets into evening — lights in the windows, trees and lawn in the half-light, and the place we share still welcoming under the open sky.',
  },
  {
    title: 'Life in Bloom',
    subtitle:
      'Like the gardens we tend, our work grows with patience, colour, and hope — together in Odisha and beyond.',
  },
]

function collectLegacyHeroImages(data) {
  const images = []
  const seen = new Set()
  const add = (url, responsive) => {
    if (!url || seen.has(url)) return
    seen.add(url)
    images.push({ image: url, responsive: responsive || null })
  }

  add(data?.banner_image, data?.banner_image_responsive)
  for (const photo of data?.hero_photos || []) add(photo?.picture, photo?.picture_responsive)
  return images
}

function buildHeroSlides(data) {
  const legacyImages = collectLegacyHeroImages(data)
  const fromApi = data?.hero_slides

  if (fromApi?.length) {
    return fromApi.map((slide, slideIndex) => {
      const legacy = legacyImages[slideIndex]
      const image = slide.image || legacy?.image || HERO_FALLBACK_IMAGES[slideIndex] || null
      const responsive = slide.image ? slide.image_responsive : legacy?.responsive
      return {
        title: slide.title || DEFAULT_HERO_SLIDES[slideIndex]?.title || '',
        subtitle: slide.subtitle || DEFAULT_HERO_SLIDES[slideIndex]?.subtitle || '',
        image,
        responsive: image === HERO_FALLBACK_IMAGES[slideIndex] ? null : responsive || null,
      }
    })
  }

  return DEFAULT_HERO_SLIDES.map((slide, slideIndex) => {
    const legacy = legacyImages[slideIndex]
    const image = legacy?.image || HERO_FALLBACK_IMAGES[slideIndex] || null
    return {
      ...slide,
      image,
      responsive: image === HERO_FALLBACK_IMAGES[slideIndex] ? null : legacy?.responsive || null,
    }
  })
}

export default function Hero({ data }) {
  const [index, setIndex] = useState(0)
  const logoUrl = data?.logo_url || null
  const slides = useMemo(() => buildHeroSlides(data), [data])

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
                    srcSet={s.responsive?.srcset || undefined}
                    sizes={s.responsive ? '(min-width: 1024px) 50vw, 100vw' : undefined}
                    width={s.responsive?.width || undefined}
                    height={s.responsive?.height || undefined}
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
              <div className="flex items-center justify-center gap-3.5">
                {slides.map((_, i) => (
                  <button
                    key={`mobile-dot-${String(i)}`}
                    type="button"
                    role="tab"
                    aria-selected={i === index}
                    aria-label={`Slide ${i + 1}`}
                    className="relative flex items-center justify-center py-[17px] px-[3px] -my-[17px] -mx-[3px]"
                    onClick={() => setIndex(i)}
                  >
                    <span
                      className={`h-2.5 rounded-full transition-all duration-300 ${
                        i === index
                          ? 'w-8 bg-[#005E66] shadow-sm'
                          : 'w-2.5 bg-slate-300 hover:bg-slate-400'
                      }`}
                    />
                  </button>
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
              <h1
                className="mb-4 w-full font-sans text-xl font-bold leading-tight tracking-tight text-slate-900 max-lg:text-center sm:mb-5 sm:text-2xl md:text-3xl lg:text-left lg:text-[clamp(1.625rem,0.35rem+2.35vw,2.125rem)] xl:text-[clamp(1.75rem,0.5rem+2.1vw,2.35rem)]"
                dangerouslySetInnerHTML={{ __html: slide.title }}
              />
              <div
                className="w-full max-w-xl max-lg:mx-auto max-lg:text-center font-sans text-[0.9375rem] leading-relaxed text-slate-700 sm:text-base md:text-lg lg:mx-0 lg:text-left [&_p]:mb-3 [&_p:last-child]:mb-0 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_a]:underline"
                dangerouslySetInnerHTML={{ __html: slide.subtitle }}
              />
            </div>
            <div className="mt-10 hidden w-full justify-start lg:flex lg:mt-0 lg:pt-4">
              <div
                className="flex items-center justify-center gap-3.5"
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
                    className="relative flex items-center justify-center py-[17px] px-[3px] -my-[17px] -mx-[3px]"
                    onClick={() => setIndex(i)}
                  >
                    <span
                      className={`h-2.5 rounded-full transition-all duration-300 ${
                        i === index
                          ? 'w-8 bg-[#005E66] shadow-sm'
                          : 'w-2.5 bg-slate-300 hover:bg-slate-400'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
