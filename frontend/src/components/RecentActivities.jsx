import { useState } from 'react'

export default function RecentActivities({ data }) {
  const events = data?.recent_events || []
  const [selected, setSelected] = useState(null)
  if (events.length === 0) return null

  const formatDate = (d) => {
    if (!d) return ''
    const date = new Date(d)
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  return (
    <section id="recent-activities" className="landing-section bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <h2 className="section-title text-center">Recent Activities</h2>
        <div className="section-title-accent mb-8" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => (
            <div
              key={event.id}
              className="rounded-2xl overflow-hidden bg-white border-t-4 border-teal border-2 border-teal/25 shadow-[var(--card-shadow)] landing-card cursor-pointer"
              onClick={() => setSelected(event)}
            >
                <div className="aspect-video bg-teal-pale/50 overflow-hidden">
                {event.thumb ? (
                  <img src={event.thumb} alt={event.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-teal font-heading">
                    {event.name}
                  </div>
                )}
              </div>
              <div className="p-5">
                <h3 className="font-heading font-semibold text-teal-deep">{event.name}</h3>
                <p className="text-sm text-slate-700 mt-1 font-medium">{event.source}</p>
                <p className="text-sm text-slate-600 mt-2">{formatDate(event.date)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/60"
          onClick={() => setSelected(null)}
        >
<div
          className="bg-white rounded-t-2xl sm:rounded-2xl max-w-lg w-full max-h-[min(92dvh,640px)] sm:max-h-[90vh] overflow-y-auto shadow-[var(--card-shadow-hover)] border border-teal/20"
          onClick={(e) => e.stopPropagation()}
        >
            <div className="p-4 sm:p-6">
              <div className="flex justify-between items-start mb-4 gap-3">
                <h3 className="font-heading font-bold text-lg sm:text-xl text-teal-deep">{selected.name}</h3>
                <button
                  type="button"
                  className="text-slate-600 hover:text-teal-deep"
                  onClick={() => setSelected(null)}
                  aria-label="Close"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <p className="text-sm text-teal-deep mb-4 font-medium">{formatDate(selected.date)} · {selected.source}</p>
              {selected.thumb && (
                <img src={selected.thumb} alt={selected.name} className="mb-4 w-full rounded-2xl" />
              )}
              <p className="font-body text-slate-700 whitespace-pre-wrap leading-relaxed">{selected.description}</p>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
