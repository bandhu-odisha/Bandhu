import { useMemo, useEffect, useState, useCallback } from 'react'
import Navbar from './components/Navbar'
import { CTA_PILL_CLASS } from './cta'

/** Past this scroll offset, navbar hides until user hovers the top strip or scrolls back to top. */
const NAV_SCROLL_TOP_THRESHOLD = 10
import LoginModal from './components/LoginModal'
import Hero from './components/Hero'
import About from './components/About'
import Mission from './components/Mission'
import RecentActivities from './components/RecentActivities'
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
  const auth = data?.auth_modal
  const isAuthed = data?.user?.is_authenticated
  const signupHref = data?.urls?.signup || '/accounts/signup/'
  const [scrollY, setScrollY] = useState(0)
  const [peekNav, setPeekNav] = useState(false)
  const [loginOpen, setLoginOpen] = useState(
    () =>
      !!(
        auth &&
        (auth.open_from_url || (typeof auth.err_code === 'number' && auth.err_code > 0))
      )
  )

  const openLogin = useCallback(() => setLoginOpen(true), [])
  const closeLogin = useCallback(() => setLoginOpen(false), [])

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
          <div
            className="fixed top-0 left-0 right-0 z-[60] h-12 bg-transparent"
            aria-hidden
            onMouseEnter={() => setPeekNav(true)}
          />
        )}
        <div
          className={`w-full bg-white shadow-[0_1px_0_rgba(15,23,42,0.06)] transition-transform duration-300 ease-out motion-reduce:transition-none ${
            showNav ? 'translate-y-0' : '-translate-y-full pointer-events-none'
          }`}
          onMouseEnter={() => {
            if (navHiddenByScroll) setPeekNav(true)
          }}
          onMouseLeave={onNavBarMouseLeave}
        >
          <Navbar data={data} onOpenLogin={openLogin} />
        </div>
      </header>
      {!isAuthed && (
        <LoginModal
          open={loginOpen}
          onClose={closeLogin}
          loginUrl={data.urls?.login || '/accounts/login/'}
          signupUrl={data.urls?.signup || '/accounts/signup/'}
          csrfToken={data.csrf_token}
          authModal={auth}
        />
      )}
      <main className="pt-[5.25rem] sm:pt-20 flex flex-col">
        <Hero />
        <Mission data={data} />
        {data.videos?.length > 0 && <Videos data={data} />}
        {data.recent_events?.length > 0 && <RecentActivities data={data} />}
        <Gallery data={data} />
        <OurVisitors />
        {data.about && <About data={data} />}
      </main>
      <a
        href={signupHref}
        className={`fixed bottom-5 right-5 z-[160] shadow-[0_12px_30px_rgba(0,94,102,0.32)] hover:shadow-[0_16px_36px_rgba(0,94,102,0.4)] sm:bottom-7 sm:right-7 ${CTA_PILL_CLASS}`}
        style={{ marginBottom: 'max(0.25rem, env(safe-area-inset-bottom, 0px))' }}
      >
        Be a Bandhu
      </a>
      <Footer data={data} />
    </div>
  )
}
