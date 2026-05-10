import { useState, useEffect } from 'react'

/** Two-column hero: headline + subtitle + carousel dots; image card with shadow. */
const HERO_SLIDE_MS = 6000

const HERO_SLIDES = [
  {
    title: 'The Friend of the Last Man',
    subtitle:
      'Bandhu is an idea that celebrates goodness — in you, me, and all others. Friendship, sincerity, and small acts that matter.',
    image: '/static/img/our_mission.jpg',
  },
  {
    title: 'Goodness in Every Direction',
    subtitle:
      'We are people who care about what is inconsistent within and without — and who choose to do small things with the highest sincerity.',
    image: '/static/img/our_mission1.jpg',
  },
  {
    title: 'Bandhu at twilight',
    subtitle:
      'The campus quiets into evening — lights in the windows, trees and lawn in the half-light, and the place we share still welcoming under the open sky.',
    image: '/static/img/about-slide-3-campus.png',
  },
  {
    title: 'Life in Bloom',
    subtitle:
      'Like the gardens we tend, our work grows with patience, colour, and hope — together in Odisha and beyond.',
    image: '/static/img/about-slide-2-hibiscus.png',
  },
]

export default function Hero() {
  const [index, setIndex] = useState(0)
  const logoUrl = '/static/img/bandhu-logo-navbar.png'

  useEffect(() => {
    if (HERO_SLIDES.length <= 1) return undefined
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % HERO_SLIDES.length)
    }, HERO_SLIDE_MS)
    return () => window.clearInterval(id)
  }, [])

  const slide = HERO_SLIDES[index]

  return (
    <section
      id="top"
      className="relative overflow-hidden bg-white"
      aria-roledescription="carousel"
      aria-label="Bandhu highlights"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14 lg:py-16">
        <div className="grid lg:grid-cols-2 gap-10 lg:gap-12 xl:gap-16 lg:items-stretch">
          {/* Left: copy vertically centered; left-aligned text; dots pinned to bottom on lg */}
          <div className="order-2 lg:order-1 flex min-h-0 flex-col text-left lg:h-full">
            <div className="flex min-h-0 flex-1 flex-col justify-center lg:py-2">
              <div className="mb-7 flex items-center gap-4 sm:mb-8 sm:gap-6">
                <img
                  src={logoUrl}
                  alt="Bandhu logo"
                  className="h-24 w-24 shrink-0 object-contain sm:h-28 sm:w-28"
                  width={112}
                  height={112}
                />
                <h2 className="font-serif text-5xl font-black leading-[0.92] tracking-[-0.03em] text-[#004f57] sm:text-6xl lg:text-[4.35rem] xl:text-[4.85rem]">
                  Bandhu
                </h2>
              </div>
              <h1 className="mb-4 font-serif text-2xl font-bold leading-tight tracking-tight text-slate-900 sm:mb-5 sm:text-3xl lg:text-[clamp(1.625rem,0.35rem+2.35vw,2.125rem)] xl:text-[clamp(1.75rem,0.5rem+2.1vw,2.35rem)]">
                {slide.title}
              </h1>
              <p className="max-w-xl font-serif text-base leading-relaxed text-slate-700 sm:text-lg">
                {slide.subtitle}
              </p>
            </div>
            <div className="mt-10 flex w-full justify-start lg:mt-0 lg:pt-4">
              <div
                className="flex items-center justify-center gap-2"
                role="tablist"
                aria-label="Hero slides"
              >
                {HERO_SLIDES.map((_, i) => (
                  <button
                    key={String(i)}
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

          {/* Right: image only (no border frame). */}
          <div className="order-1 lg:order-2 w-full max-w-lg mx-auto lg:max-w-none lg:mx-0">
            <div className="relative rounded-2xl overflow-hidden bg-slate-100 aspect-[4/3] shadow-[0_10px_28px_rgba(15,23,42,0.12)]">
              {HERO_SLIDES.map((s, i) => (
                <img
                  key={s.image}
                  src={s.image}
                  alt=""
                  className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-out ${
                    i === index ? 'opacity-100 z-[1]' : 'opacity-0 z-0'
                  }`}
                  loading={i === 0 ? 'eager' : 'lazy'}
                  decoding="async"
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
