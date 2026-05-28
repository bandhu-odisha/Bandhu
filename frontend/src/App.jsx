import { useMemo, useEffect, useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import BeABandhuFab from './components/BeABandhuFab'

/** Past this scroll offset, navbar hides until user hovers the top strip or scrolls back to top. */
const NAV_SCROLL_TOP_THRESHOLD = 10
import Hero from './components/Hero'
import About from './components/About'
import Mission from './components/Mission'
import Gallery from './components/Gallery'
import OurVisitors from './components/OurVisitors'
import Videos from './components/Videos'
import Footer from './components/Footer'

function getLandingData() {
  const el = document.getElementById('landing-data')
  if (!el || !el.textContent) return null
  try {
    return JSON.parse(el.textContent)
  } catch {
    return null
  }
}

function isInsidePortaledNavDropdown(node) {
  if (!node || !(node instanceof Element)) return false
  return Boolean(
    node.closest(
      '[data-mission-dropdown], [data-support-dropdown], [data-notice-dropdown]'
    )
  )
}

export default function App() {
  const data = useMemo(getLandingData, [])
  const signupHref = data?.urls?.signup || '/accounts/signup/'
  const [scrollY, setScrollY] = useState(0)
  const [peekNav, setPeekNav] = useState(false)

  useEffect(() => {
    const onScroll = () => {
      setScrollY(window.scrollY || document.documentElement.scrollTop)
      setPeekNav(false)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const atTop = scrollY <= NAV_SCROLL_TOP_THRESHOLD
  const navHiddenByScroll = !atTop
  const showNav = atTop || peekNav

  const onNavBarMouseLeave = useCallback(
    (e) => {
      if (!navHiddenByScroll) return
      const next = e.relatedTarget
      if (isInsidePortaledNavDropdown(next)) return
      if (next && e.currentTarget.contains(next)) return
      setPeekNav(false)
    },
    [navHiddenByScroll]
  )

  // When landing with #mission (e.g. from "Back to Our Mission"), scroll to the mission section
  useEffect(() => {
    if (!data || window.location.hash !== '#mission') return
    const scrollToMission = () => {
      const el = document.getElementById('mission')
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
    const t = requestAnimationFrame(() => {
      requestAnimationFrame(scrollToMission)
    })
    return () => cancelAnimationFrame(t)
  }, [data])

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <p className="text-slate-500">Loading…</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <header className="fixed top-0 left-0 right-0 z-50 w-full">
        {navHiddenByScroll && !showNav && (
          <button
            type="button"
            className="fixed top-0 left-0 right-0 z-[60] h-14 sm:h-12 bg-transparent touch-manipulation cursor-pointer"
            aria-label="Show navigation"
            onMouseEnter={() => setPeekNav(true)}
            onFocus={() => setPeekNav(true)}
            onClick={() => setPeekNav(true)}
          />
        )}
        <div
          className={`w-full bg-white shadow-[0_1px_0_rgba(15,23,42,0.06)] transition-transform duration-300 ease-out motion-reduce:transition-none ${
            showNav ? 'translate-y-0' : '-translate-y-full'
          }`}
          onMouseEnter={() => {
            if (navHiddenByScroll) setPeekNav(true)
          }}
          onMouseLeave={onNavBarMouseLeave}
        >
          <Navbar data={data} />
        </div>
      </header>
      <main className="pt-[5.25rem] sm:pt-20 flex flex-col">
        <Hero data={data} />
        <Mission data={data} />
        {data.videos?.length > 0 && <Videos data={data} />}
        <Gallery data={data} />
        <OurVisitors data={data} />
        {data.about && <About data={data} />}
      </main>
      {!data?.user?.is_authenticated && <BeABandhuFab href={signupHref} />}
      <Footer data={data} />
    </div>
  )
}
