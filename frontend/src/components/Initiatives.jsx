function stripHtml(html) {
  if (!html || typeof html !== 'string') return ''
  return html.replace(/<[^>]*>/g, '').trim()
}

export default function Initiatives({ data }) {
  const initiatives = data?.initiatives
  const urls = data?.urls || {}
  if (!initiatives) return null

  const allCards = [
    { key: 'ankurayan', title: 'Ankurayan', href: urls.ankurayan, thumb: initiatives.ankurayan_thumb, desc: initiatives.ankurayan_desc },
    { key: 'kendra', title: 'Anandakendra', href: urls.anandakendra, thumb: initiatives.kendra_thumb, desc: initiatives.kendra_desc },
    { key: 'bandhughar', title: 'Bandhughar', href: urls.ashram, thumb: initiatives.bandhughar_thumb, desc: initiatives.bandhughar_desc },
    { key: 'other', title: 'Other Activities', href: urls.charity_work, thumb: initiatives.otheract_thumb, desc: initiatives.otheract_desc },
    { key: 'publications', title: 'Our Publications', href: urls.publications, thumb: initiatives.publications_thumb, desc: initiatives.publications_desc },
  ]

  return (
    <section id="initiatives" className="py-10 sm:py-14 bg-white">
      <div className="max-w-[90rem] mx-auto px-6 sm:px-8">
        <h2 className="section-title text-center mb-6">
          Support a Cause
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 md:gap-8">
          {allCards.map((card) => (
            <a
              key={card.key}
              href={card.href || '#'}
              className="group block overflow-hidden rounded-2xl border border-gray-200/80 bg-white no-underline transition-all duration-300 ease-out hover:-translate-y-2 hover:no-underline hover:shadow-xl hover:shadow-teal/10 hover:border-teal/30 focus:outline-none focus:no-underline focus:ring-2 focus:ring-teal/40 focus:ring-offset-2"
            >
              <div className="relative aspect-[4/3] min-h-[220px] overflow-hidden">
                <img
                  src={card.thumb}
                  alt={card.title}
                  className="w-full h-full object-cover transition-transform duration-500 ease-out group-hover:scale-110"
                />
                <div
                  className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent transition-opacity duration-300 group-hover:opacity-80"
                  aria-hidden
                />
                <h3 className="absolute bottom-0 left-0 right-0 p-4 font-heading font-bold text-white text-lg sm:text-xl uppercase tracking-tight text-center opacity-100 group-hover:opacity-0 transition-opacity duration-300">
                  {card.title}
                </h3>
              </div>
              <div className="p-4 sm:p-5 border-t border-gray-100 text-center">
                <p className="font-body text-sm text-black leading-relaxed line-clamp-3">
                  {stripHtml(card.desc || '').slice(0, 160)}
                  {stripHtml(card.desc || '').length > 160 ? '…' : ''}
                </p>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
