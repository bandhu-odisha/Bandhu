import { useMemo } from 'react'
import { CTA_PILL_CLASS } from '../cta'

const MISSION_STATEMENT = 'We work to strengthen the self-worth and dignity of people across villages and cities in India, and to support them as equal partners, so they can draw on their own strengths and potential to meet the challenges they face.'

/** Card excerpt cap — one pass at word boundary in concisePillarText (no second arbitrary slice). */
const PILLAR_TEXT_MAX_LENGTH = 220

function stripHtml(html) {
  if (!html || typeof html !== 'string') return ''
  return html.replace(/<[^>]*>/g, '').trim()
}

/** Strip legacy CMS noise from mission pillar blurbs (stored copy may still contain this). */
function removePillarBoilerplate(s) {
  if (!s || typeof s !== 'string') return s
  return s
    // Sanskar CMS: "education successfully. More importantly, this initiative aims to ensure a supportive …"
    .replace(
      /\beducation successfully\.\s*More importantly,\s*this initiative aims to ensure a supportive[^.]*\.?/gi,
      ' '
    )
    // ". Successfully, not only in terms of good marks …" (CMS variants end mid-sentence or with "…awareness.")
    .replace(/\.\s*Successfully,\s*not only in terms of good marks[^.]*\.?/gi, '.')
    .replace(
      /education successfully\.\s*Successfully,\s*not only in terms of good marks in the AND through empowerment and awareness\.?/gi,
      ' education successfully.'
    )
    .replace(
      /Successfully,\s*not only in terms of good marks in the AND through empowerment and awareness\.?/gi,
      ' '
    )
    .replace(/\s+/g, ' ')
    .trim()
}

function concisePillarText(tagline, desc) {
  const combinedRaw = [tagline, desc].filter(Boolean).map(stripHtml).join(' ').replace(/\s+/g, ' ').trim()
  const combined = removePillarBoilerplate(combinedRaw)
  if (!combined) return ''
  const normalized = combined
    // Replace repeated dots with commas for cleaner prose.
    .replace(/\.{2,}/g, ', ')
    .replace(/\s+,/g, ',')
    .replace(/,\s*,+/g, ', ')
    .replace(/\s+/g, ' ')
    .trim()
  if (normalized.length <= PILLAR_TEXT_MAX_LENGTH) return normalized
  return normalized.slice(0, PILLAR_TEXT_MAX_LENGTH).trim().replace(/\s+\S*$/, '')
}

export default function Mission({ data }) {
  const mission = data?.mission
  const urls = data?.urls || {}

  const pillars = useMemo(() => {
    const getImage = (imgs) => (imgs?.length ? imgs[0].picture : null)
    return [
      {
        id: 'sanskar',
        title: 'Sanskar',
        tagline: mission?.sanskar_tagline,
        desc: mission?.sanskar_desc,
        image: getImage(mission?.sanskar_images),
        href: urls.sanskar || '#',
      },
      {
        id: 'swaraj',
        title: 'Swaraj',
        tagline: mission?.swaraj_tagline,
        desc: mission?.swaraj_desc,
        image: getImage(mission?.swaraj_images),
        href: urls.swaraj || '#',
      },
      {
        id: 'swabalamban',
        title: 'Swabalamban',
        tagline: mission?.swabalamban_tagline,
        desc: mission?.swabalamban_desc,
        image: getImage(mission?.swabalamban_images),
        href: urls.swabalamban || '#',
      },
    ]
  }, [mission, urls])

  return (
    <section id="mission" className="landing-section bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        {/* Mission intro — text-first, centered (no hero photo). */}
        <div className="pt-2 pb-10 sm:pb-14 md:pb-16 text-center">
          <h2 className="font-body font-black normal-case tracking-normal text-[clamp(2.25rem,6.5vw,3.85rem)] leading-snug word-spacing-[0.12em] mb-6 sm:mb-8">
            <span className="text-[#005E66]">Our</span>{' '}
            <span className="text-[#0b3540]">Mission</span>
          </h2>
          <p className="font-body text-[#3d5c66] text-lg sm:text-xl md:text-[1.35rem] leading-relaxed max-w-3xl mx-auto mb-8 sm:mb-10">
            {MISSION_STATEMENT}
          </p>
          <div className="flex justify-center">
            <a href="#pillars" className={CTA_PILL_CLASS}>
              Learn More
            </a>
          </div>
        </div>
      </div>

      {/* Full-bleed band: same cool gray as Volunteer; content stays max-w-6xl. */}
      <div
        id="pillars"
        className="mt-2 sm:mt-4 w-full scroll-mt-[5.25rem] bg-slate-100/95"
      >
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-10">
          <h3 className="section-title text-left mb-10 sm:mb-12">
            Our pillars of change
          </h3>
          <div>
            {pillars.map((pillar, idx) => {
              const isSanskar = pillar.id === 'sanskar'
              const isSwaraj = pillar.id === 'swaraj'
              const cardText = concisePillarText(pillar.tagline, pillar.desc)
              const cleanedCardText = isSanskar
                ? cardText.replace(/^Anandakendra and Ankurayan\s*/i, '').trim()
                : cardText
              const taglineText = stripHtml(pillar.tagline || '')
              const summaryLine = taglineText || cleanedCardText
              const detailsLine =
                cleanedCardText && cleanedCardText !== summaryLine ? cleanedCardText : ''
              const fallbackImages = {
                sanskar: '/static/img/our_mission.jpg',
                swaraj: '/static/img/our_mission1.jpg',
                swabalamban: '/static/img/pimg2.jpg',
              }
              const imageSrc = pillar.image || fallbackImages[pillar.id] || null

              return (
                <a
                  key={pillar.id}
                  href={pillar.href}
                  className={`group grid grid-cols-1 md:grid-cols-[1.05fr_1fr] gap-6 md:gap-10 items-center py-10 md:py-14 no-underline hover:no-underline focus:no-underline ${
                    idx < pillars.length - 1 ? 'border-b border-slate-400/75' : ''
                  }`}
                >
                  <div className={isSwaraj ? 'order-1 md:order-2' : 'order-2 md:order-1'}>
                    <h4 className="font-heading font-bold text-3xl text-[#0b3540] mb-2 no-underline">
                      {pillar.title}
                    </h4>
                    <p className="font-body text-lg text-[#1c3f49] font-semibold leading-snug mb-1.5 no-underline">
                      {summaryLine}
                    </p>
                    {detailsLine && (
                      <p className="font-body text-lg text-[#2d4c55] leading-relaxed max-w-[60ch] line-clamp-3 no-underline">
                        {detailsLine}
                      </p>
                    )}
                    <span className="mt-3 inline-block font-body text-sm font-semibold tracking-wide uppercase text-[#0b3540] underline underline-offset-[3px] decoration-[#0b3540]/80 group-hover:text-[#005E66] group-hover:decoration-[#005E66]">
                      Explore →
                    </span>
                  </div>

                  <div className={isSwaraj ? 'order-2 md:order-1' : 'order-1 md:order-2'}>
                    <div className="aspect-[16/9] overflow-hidden rounded-2xl bg-white/80">
                      {imageSrc ? (
                        <img
                          src={imageSrc}
                          alt={pillar.title}
                          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
                        />
                      ) : null}
                    </div>
                  </div>
                </a>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
