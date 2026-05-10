import { useState, useEffect, useRef } from 'react'

const AUTO_SCROLL_INTERVAL_MS = 5000
/** Match Tailwind `gap-10` (2.5rem) for auto-scroll step. */
const GAP_PX = 40
const CARD_WIDTH_FALLBACK = 440

function getYouTubeId(script) {
  if (!script || typeof script !== 'string') return null
  let m = script.match(/(?:youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})/)
  if (m) return m[1]
  m = script.match(/youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/)
  if (m) return m[1]
  m = script.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/)
  if (m) return m[1]
  m = script.match(/[\?&]v=([a-zA-Z0-9_-]{11})/)
  if (m) return m[1]
  return null
}

function thumbnailUrl(videoId) {
  return `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`
}

function VideoCard({ video, onClick }) {
  const [thumbError, setThumbError] = useState(false)
  const showThumb = video.videoId && !thumbError
  const duration =
    video.duration != null && String(video.duration).trim() !== ''
      ? String(video.duration).trim()
      : ''

  return (
    <div className="flex-shrink-0 w-[320px] sm:w-[380px] group snap-start" data-video-card>
      <button
        type="button"
        onClick={onClick}
        className="w-full text-left rounded-2xl overflow-hidden bg-white shadow-[var(--card-shadow)] hover:shadow-[var(--card-shadow-hover)] transition-all duration-300 border border-teal/20 focus:outline-none focus:ring-2 focus:ring-teal focus:ring-offset-2"
      >
        <div className="relative aspect-video bg-slate-100">
          {showThumb ? (
            <img
              src={thumbnailUrl(video.videoId)}
              alt={video.title}
              className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
              loading="lazy"
              onError={() => setThumbError(true)}
            />
          ) : (
            <div className="flex h-full w-full items-center justify-center bg-teal-pale">
              <span className="font-body text-sm text-teal-dark/50">Video</span>
            </div>
          )}
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/15 transition group-hover:bg-black/25">
            <svg
              className="h-10 w-10 text-white drop-shadow-[0_2px_8px_rgba(0,0,0,0.45)] transition-transform duration-300 group-hover:scale-110 sm:h-12 sm:w-12"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
          {duration ? (
            <span className="pointer-events-none absolute bottom-2 right-2 z-20 font-body text-xs font-semibold tabular-nums text-white sm:text-sm [text-shadow:0_1px_2px_rgba(0,0,0,0.9),0_0_10px_rgba(0,0,0,0.45)]">
              {duration}
            </span>
          ) : null}
        </div>
        <p className="truncate bg-white p-4 font-body text-base font-semibold text-teal-deep">{video.title}</p>
      </button>
    </div>
  )
}

export default function Videos({ data }) {
  const videos = data?.videos || []
  const [playing, setPlaying] = useState(null)
  const scrollRef = useRef(null)
  const n = videos.length
  if (n === 0) return null

  const withIds = videos.map((v) => ({
    ...v,
    videoId: v.video_id || getYouTubeId(v.script),
    duration: v.duration != null && v.duration !== '' ? String(v.duration).trim() : '',
  }))

  useEffect(() => {
    if (n <= 1) return
    const el = scrollRef.current
    if (!el) return
    const id = setInterval(() => {
      const firstCard = el.querySelector('[data-video-card]')
      const cardWidth = firstCard ? firstCard.offsetWidth : CARD_WIDTH_FALLBACK
      const step = cardWidth + GAP_PX
      const maxScroll = el.scrollWidth - el.clientWidth
      if (maxScroll <= 0) return
      const current = el.scrollLeft
      const nextIndex = Math.round(current / step) + 1
      let next = nextIndex * step
      if (next >= maxScroll) next = 0
      el.scrollTo({ left: next, behavior: 'smooth' })
    }, AUTO_SCROLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [n])

  return (
    <section id="youtube" className="landing-section bg-white -mt-10 sm:-mt-12 lg:-mt-14">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <h2 className="section-title text-center mb-8">Stories in Motion</h2>
        <div
          ref={scrollRef}
          className="mx-auto w-[1040px] max-w-full overflow-x-auto overflow-y-hidden scrollbar-hide scroll-smooth snap-x snap-mandatory sm:w-[1180px]"
        >
          <div className="flex w-max gap-4">
            {withIds.map((video, i) => (
              <VideoCard key={i} video={video} onClick={() => setPlaying(playing === i ? null : i)} />
            ))}
          </div>
        </div>
        {playing !== null && withIds[playing] && (
          <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm"
            onClick={() => setPlaying(null)}
          >
            <div
              className="relative aspect-video w-full max-w-4xl overflow-hidden rounded-2xl bg-black shadow-2xl"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-teal-dark hover:bg-white"
                onClick={() => setPlaying(null)}
                aria-label="Close"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <div
                className="h-full w-full [&>iframe]:h-full [&>iframe]:w-full"
                dangerouslySetInnerHTML={{ __html: withIds[playing].script }}
              />
              <p className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 font-body font-semibold text-white">
                {withIds[playing].title}
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
