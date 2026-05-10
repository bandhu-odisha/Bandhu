import { useState, useEffect } from 'react'

const ABOUT_SLIDES = [
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

const SLIDE_MS = 5000

export default function About({ data }) {
  const about = data?.about
  const [slideIndex, setSlideIndex] = useState(0)

  useEffect(() => {
    if (ABOUT_SLIDES.length <= 1) return undefined
    const id = window.setInterval(() => {
      setSlideIndex((i) => (i + 1) % ABOUT_SLIDES.length)
    }, SLIDE_MS)
    return () => window.clearInterval(id)
  }, [])

  if (!about) return null

  return (
    <section id="about" className="landing-section bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <h2 className="section-title text-center mb-8 sm:mb-10">About Us</h2>

        <div className="grid lg:grid-cols-2 gap-6 lg:gap-8 xl:gap-10 items-stretch">
          <div className="order-2 lg:order-1 flex min-h-0 lg:-ml-2 xl:-ml-4 2xl:-ml-5">
            <div className="rounded-2xl bg-white w-full py-8 sm:py-12 pl-0 pr-4 sm:pr-6 lg:pr-8 text-left lg:h-full lg:flex lg:flex-col lg:justify-center">
              <p
                className="font-body font-bold text-[#0b3540] text-lg sm:text-xl md:text-[1.28rem] lg:text-[1.34rem] leading-snug tracking-tight mb-6 sm:mb-7 [&_a]:text-[#005E66] [&_a]:underline"
                dangerouslySetInnerHTML={{ __html: about.tagline }}
              />
              <p
                className="font-body font-normal text-[#3d5c66] text-base sm:text-lg md:text-[1.2rem] lg:text-[1.26rem] leading-relaxed w-full [&_a]:text-[#005E66] [&_a]:underline"
                dangerouslySetInnerHTML={{ __html: about.desc }}
              />
            </div>
          </div>

          <div className="order-1 lg:order-2 w-full min-h-0 flex flex-col lg:h-full">
            <figure className="m-0 flex flex-col flex-1 min-h-0 w-full">
              <div
                className="relative w-full aspect-[5/4] sm:aspect-[4/3] min-h-[13rem] lg:aspect-auto lg:flex-1 lg:min-h-[12rem] rounded-2xl overflow-hidden border border-black/[0.08] bg-slate-100"
                aria-live="polite"
                aria-atomic="true"
              >
                {ABOUT_SLIDES.map((slide, i) => (
                  <img
                    key={slide.src}
                    src={slide.src}
                    alt=""
                    className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-700 ease-out ${
                      i === slideIndex ? 'opacity-100 z-[1]' : 'opacity-0 z-0'
                    }`}
                    loading={i === 0 ? 'eager' : 'lazy'}
                  />
                ))}
              </div>
              <figcaption className="mt-4 pl-0 pr-1 shrink-0">
                <p className="font-body text-sm sm:text-base text-slate-600 leading-snug text-left min-h-[3rem] sm:min-h-[3.25rem]">
                  {ABOUT_SLIDES[slideIndex].caption}
                </p>
                <div
                  className="flex justify-start gap-1.5 mt-3"
                  role="tablist"
                  aria-label="Photo carousel position"
                >
                  {ABOUT_SLIDES.map((_, i) => (
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
    </section>
  )
}
