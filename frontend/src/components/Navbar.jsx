import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { LANDING_NAVBAR_AUTH_BUTTON_CLASS } from '../cta'
import CurrentUpdates from './CurrentUpdates'

/** Links inside the floating nav pill — flat hover, no heavy chrome. */
const NAV_LINK =
  'font-body text-sm font-medium text-slate-700 no-underline hover:text-slate-900 hover:no-underline focus:no-underline whitespace-nowrap py-1.5 px-1 sm:px-1.5 inline-flex items-center gap-1 rounded-lg transition-colors duration-200 hover:bg-slate-100/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#005E66]/30 focus-visible:ring-offset-1'

const ChevronDown = ({ open }) => (
  <svg
    className={`w-3.5 h-3.5 shrink-0 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    fill="none"
    stroke="currentColor"
    strokeWidth={2}
    viewBox="0 0 24 24"
    aria-hidden
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
  </svg>
)

export default function Navbar({ data }) {
  const urls = data?.urls || {}
  const user = data?.user || {}
  const initialNotices = data?.recent_activities ?? []
  const [notices, setNotices] = useState(initialNotices)
  const [noticesLoading, setNoticesLoading] = useState(initialNotices.length === 0)
  const [noticeOpen, setNoticeOpen] = useState(false)
  const noticeRef = useRef(null)
  const noticeDropdownRef = useRef(null)
  const [dropdownRect, setDropdownRect] = useState(null)
  const [missionOpen, setMissionOpen] = useState(false)
  const missionRef = useRef(null)
  const [missionDropdownRect, setMissionDropdownRect] = useState(null)
  const [supportOpen, setSupportOpen] = useState(false)
  const supportRef = useRef(null)
  const [supportDropdownRect, setSupportDropdownRect] = useState(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [drawerMissionOpen, setDrawerMissionOpen] = useState(false)
  const [drawerSupportOpen, setDrawerSupportOpen] = useState(false)
  const [drawerNoticeOpen, setDrawerNoticeOpen] = useState(false)

  const closeMobileMenu = () => {
    setMobileMenuOpen(false)
    setDrawerMissionOpen(false)
    setDrawerSupportOpen(false)
    setDrawerNoticeOpen(false)
  }

  useEffect(() => {
    if (initialNotices.length > 0) {
      setNotices(initialNotices)
      setNoticesLoading(false)
      return
    }
    let cancelled = false
    setNoticesLoading(true)
    fetch('/api/landing/')
      .then((res) => (res.ok ? res.json() : null))
      .then((json) => {
        if (!cancelled && json && Array.isArray(json.recent_activities)) {
          setNotices(json.recent_activities)
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setNoticesLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [initialNotices.length])

  const updateDropdownRect = () => {
    if (noticeRef.current) {
      const rect = noticeRef.current.getBoundingClientRect()
      const w = 320
      const left = Math.max(8, Math.min(rect.right - w, document.documentElement.clientWidth - w - 8))
      setDropdownRect({ top: rect.bottom + 4, left, width: w })
    }
  }

  const updateMissionDropdownRect = () => {
    if (missionRef.current) {
      const rect = missionRef.current.getBoundingClientRect()
      const w = 200
      const left = Math.max(8, Math.min(rect.right - w, document.documentElement.clientWidth - w - 8))
      setMissionDropdownRect({ top: rect.bottom + 4, left, width: w })
    }
  }

  const updateSupportDropdownRect = () => {
    if (supportRef.current) {
      const rect = supportRef.current.getBoundingClientRect()
      const w = 220
      const left = Math.max(8, Math.min(rect.right - w, document.documentElement.clientWidth - w - 8))
      setSupportDropdownRect({ top: rect.bottom + 4, left, width: w })
    }
  }

  useEffect(() => {
    if (!noticeOpen) {
      setDropdownRect(null)
      return
    }
    updateDropdownRect()
    const onResize = () => updateDropdownRect()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [noticeOpen])

  useEffect(() => {
    if (!noticeOpen) return undefined
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [noticeOpen])

  useEffect(() => {
    if (!missionOpen) {
      setMissionDropdownRect(null)
      return
    }
    updateMissionDropdownRect()
    const onScrollOrResize = () => updateMissionDropdownRect()
    window.addEventListener('scroll', onScrollOrResize, true)
    window.addEventListener('resize', onScrollOrResize)
    return () => {
      window.removeEventListener('scroll', onScrollOrResize, true)
      window.removeEventListener('resize', onScrollOrResize)
    }
  }, [missionOpen])

  useEffect(() => {
    if (!supportOpen) {
      setSupportDropdownRect(null)
      return
    }
    updateSupportDropdownRect()
    const onScrollOrResize = () => updateSupportDropdownRect()
    window.addEventListener('scroll', onScrollOrResize, true)
    window.addEventListener('resize', onScrollOrResize)
    return () => {
      window.removeEventListener('scroll', onScrollOrResize, true)
      window.removeEventListener('resize', onScrollOrResize)
    }
  }, [supportOpen])

  useEffect(() => {
    if (!mobileMenuOpen) return undefined
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKey = (e) => {
      if (e.key === 'Escape') closeMobileMenu()
    }
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [mobileMenuOpen])

  useEffect(() => {
    function handleClickOutside(e) {
      const inNoticeTrigger = noticeRef.current?.contains(e.target)
      const inNoticeDropdown = document.querySelector('[data-notice-dropdown]')?.contains(e.target)
      if (!inNoticeTrigger && !inNoticeDropdown) setNoticeOpen(false)
      const inMissionTrigger = missionRef.current?.contains(e.target)
      const inMissionDropdown = document.querySelector('[data-mission-dropdown]')?.contains(e.target)
      if (!inMissionTrigger && !inMissionDropdown) setMissionOpen(false)
      const inSupportTrigger = supportRef.current?.contains(e.target)
      const inSupportDropdown = document.querySelector('[data-support-dropdown]')?.contains(e.target)
      if (!inSupportTrigger && !inSupportDropdown) setSupportOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const missionPillars = [
    { label: 'Sanskar', href: urls.sanskar || '/sanskar/' },
    { label: 'Swaraj', href: urls.swaraj || '/swaraj/' },
    { label: 'Swabalamban', href: urls.swabalamban || '/swabalamban/' },
  ]

  const initiativesLinks = [
    { label: 'Bandhughar', href: urls.ashram || '/bandhughar/' },
    { label: 'Other Activities', href: urls.charity_work || '/other_activities/' },
    { label: 'Our Publications', href: urls.publications || '/publications/' },
  ]

  const formatDate = (d) => {
    if (!d) return ''
    return new Date(d).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
  }

  const truncate = (str, max = 135) =>
    str && str.length > max ? `${str.slice(0, max).trim()}…` : str || ''

  const isolateNoticeWheel = (e) => {
    e.stopPropagation()
  }

  const MOBILE_DRAWER_LINK =
    'block w-full text-left font-body text-base font-medium text-slate-800 no-underline py-3 px-4 rounded-lg transition-colors hover:bg-slate-50 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#005E66]/30'

  const MOBILE_DRAWER_SUBLINK =
    'block w-full text-left font-body text-sm font-medium text-slate-600 no-underline py-2.5 pl-8 pr-4 rounded-lg hover:bg-slate-50 hover:text-slate-900'

  const NavLinks = () => (
    <>
      <a href={urls.home || '#top'} className={NAV_LINK}>
        Home
      </a>

      <a href={urls.people || '/people/'} className={NAV_LINK}>
        People
      </a>

      <span className="relative inline-flex" ref={missionRef}>
        <button
          type="button"
          onClick={() => setMissionOpen((o) => !o)}
          className={`${NAV_LINK} cursor-pointer border-0 bg-transparent`}
          aria-expanded={missionOpen}
          aria-haspopup="true"
        >
          Our Mission
          <ChevronDown open={missionOpen} />
        </button>
        {missionOpen &&
          missionDropdownRect &&
          createPortal(
            <div
              data-mission-dropdown
              className="fixed rounded-lg border border-black/10 bg-white shadow-xl py-1 z-[200]"
              style={{
                top: missionDropdownRect.top,
                left: missionDropdownRect.left,
                width: missionDropdownRect.width,
                minWidth: '12rem',
              }}
            >
              <ul>
                {missionPillars.map((pillar) => (
                  <li key={pillar.label}>
                    <a
                      href={pillar.href}
                      className="block px-4 py-2.5 text-left text-sm font-body font-medium text-slate-700 no-underline hover:bg-slate-50 hover:text-slate-900 hover:no-underline transition-colors"
                      onClick={() => setMissionOpen(false)}
                    >
                      {pillar.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>,
            document.body
          )}
      </span>

      <span className="relative inline-flex" ref={supportRef}>
        <button
          type="button"
          onClick={() => setSupportOpen((o) => !o)}
          className={`${NAV_LINK} cursor-pointer border-0 bg-transparent`}
          aria-expanded={supportOpen}
          aria-haspopup="true"
        >
          Initiatives
          <ChevronDown open={supportOpen} />
        </button>
        {supportOpen &&
          supportDropdownRect &&
          createPortal(
            <div
              data-support-dropdown
              className="fixed rounded-lg border border-black/10 bg-white shadow-xl py-1 z-[200]"
              style={{
                top: supportDropdownRect.top,
                left: supportDropdownRect.left,
                width: supportDropdownRect.width,
                minWidth: '14rem',
              }}
            >
              <ul>
                {initiativesLinks.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="block px-4 py-2.5 text-left text-sm font-body font-medium text-slate-700 no-underline hover:bg-slate-50 hover:text-slate-900 hover:no-underline transition-colors"
                      onClick={() => setSupportOpen(false)}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>,
            document.body
          )}
      </span>

      <a href="#contact" className={NAV_LINK}>
        Contact
      </a>

      <span className="relative inline-flex" ref={noticeRef}>
        <button
          type="button"
          onClick={() => setNoticeOpen((o) => !o)}
          className={`${NAV_LINK} cursor-pointer border-0 bg-transparent`}
          aria-expanded={noticeOpen}
          aria-haspopup="true"
        >
          Notice Board
          <ChevronDown open={noticeOpen} />
        </button>
        {noticeOpen &&
          dropdownRect &&
          createPortal(
            <div
              data-notice-dropdown
              ref={noticeDropdownRef}
              className="fixed z-[200] overflow-hidden rounded-lg border border-black/10 bg-white shadow-xl"
              style={{
                top: dropdownRect.top,
                left: dropdownRect.left,
                width: dropdownRect.width,
                minWidth: '18rem',
              }}
            >
              {noticesLoading ? (
                <p className="px-4 py-3 text-sm opacity-70 font-body">Loading…</p>
              ) : notices.length === 0 ? (
                <p className="px-4 py-3 text-sm opacity-70 font-body">No notices at the moment.</p>
              ) : (
                <ul
                  className="max-h-[min(70vh,28rem)] overflow-y-auto overscroll-contain py-1 touch-pan-y scrollbar-hide"
                  onWheel={isolateNoticeWheel}
                >
                  {notices.map((notice) => (
                    <li key={notice.id} className="border-b border-black/5 last:border-0">
                      <a
                        href={notice.link || '#'}
                        target={notice.link && notice.link !== '#' ? '_blank' : undefined}
                        rel={notice.link && notice.link !== '#' ? 'noopener noreferrer' : undefined}
                        className="group block px-4 py-3 text-left hover:bg-[#f4f6f7]"
                        onClick={() => setNoticeOpen(false)}
                      >
                        <div className="flex flex-wrap items-start justify-between gap-2">
                          <span className="font-body font-semibold text-sm text-slate-800">
                            {notice.title}
                          </span>
                          {(notice.start_date || notice.end_date) && (
                            <span className="text-xs opacity-50 shrink-0">
                              {notice.start_date && formatDate(notice.start_date)}
                              {notice.end_date &&
                                notice.start_date !== notice.end_date &&
                                ` – ${formatDate(notice.end_date)}`}
                            </span>
                          )}
                        </div>
                        {notice.description && (
                          <p className="text-xs opacity-70 mt-1 line-clamp-2 font-body">
                            {truncate(notice.description, 135)}
                          </p>
                        )}
                        {notice.link && notice.link !== '#' && (
                          <span className="inline-block mt-1.5 font-semibold text-xs text-slate-700 group-hover:text-[#005E66] transition-colors">
                            View details →
                          </span>
                        )}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </div>,
            document.body
          )}
      </span>

      {user.is_authenticated && (
        <a href="/profile/" className={NAV_LINK}>
          Profile
        </a>
      )}
    </>
  )

  const mobileMenuPanel =
    mobileMenuOpen &&
    typeof document !== 'undefined' &&
    createPortal(
      <div
        className="fixed inset-0 z-[190] md:hidden"
        role="dialog"
        aria-modal="true"
        aria-label="Site menu"
      >
        <button
          type="button"
          className="absolute inset-0 bg-slate-900/40 backdrop-blur-[1px]"
          aria-label="Close menu"
          onClick={closeMobileMenu}
        />
        <aside
          id="landing-mobile-menu"
          className="absolute top-0 left-0 flex h-full w-[min(100%,20rem)] flex-col bg-white shadow-[12px_0_40px_rgba(15,23,42,0.12)] animate-[bandhu-slide-in-left_0.25s_ease-out]"
        >
          <div className="flex shrink-0 items-center justify-between gap-3 border-b border-slate-100 px-4 py-3.5">
            <span className="font-heading text-lg font-bold text-[#005E66]">Menu</span>
            <button
              type="button"
              onClick={closeMobileMenu}
              className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 text-slate-600 hover:bg-slate-50"
              aria-label="Close menu"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <nav className="min-h-0 flex-1 overflow-y-auto overscroll-contain py-2">
            <a href={urls.home || '#top'} className={MOBILE_DRAWER_LINK} onClick={closeMobileMenu}>
              Home
            </a>
            <a href={urls.people || '/people/'} className={MOBILE_DRAWER_LINK} onClick={closeMobileMenu}>
              People
            </a>
            <button
              type="button"
              className={`${MOBILE_DRAWER_LINK} flex items-center justify-between border-0 bg-transparent cursor-pointer`}
              aria-expanded={drawerMissionOpen}
              onClick={() => setDrawerMissionOpen((o) => !o)}
            >
              Our Mission
              <ChevronDown open={drawerMissionOpen} />
            </button>
            {drawerMissionOpen && (
              <ul className="pb-1">
                {missionPillars.map((pillar) => (
                  <li key={pillar.label}>
                    <a href={pillar.href} className={MOBILE_DRAWER_SUBLINK} onClick={closeMobileMenu}>
                      {pillar.label}
                    </a>
                  </li>
                ))}
              </ul>
            )}
            <button
              type="button"
              className={`${MOBILE_DRAWER_LINK} flex items-center justify-between border-0 bg-transparent cursor-pointer`}
              aria-expanded={drawerSupportOpen}
              onClick={() => setDrawerSupportOpen((o) => !o)}
            >
              Initiatives
              <ChevronDown open={drawerSupportOpen} />
            </button>
            {drawerSupportOpen && (
              <ul className="pb-1">
                {initiativesLinks.map((link) => (
                  <li key={link.label}>
                    <a href={link.href} className={MOBILE_DRAWER_SUBLINK} onClick={closeMobileMenu}>
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            )}
            <a href="#contact" className={MOBILE_DRAWER_LINK} onClick={closeMobileMenu}>
              Contact
            </a>
            <button
              type="button"
              className={`${MOBILE_DRAWER_LINK} flex items-center justify-between border-0 bg-transparent cursor-pointer`}
              aria-expanded={drawerNoticeOpen}
              onClick={() => setDrawerNoticeOpen((o) => !o)}
            >
              Notice Board
              <ChevronDown open={drawerNoticeOpen} />
            </button>
            {drawerNoticeOpen && (
              <div className="px-2 pb-2">
                {noticesLoading ? (
                  <p className="px-4 py-2 text-sm text-slate-500 font-body">Loading…</p>
                ) : notices.length === 0 ? (
                  <p className="px-4 py-2 text-sm text-slate-500 font-body">No notices at the moment.</p>
                ) : (
                  <ul className="max-h-64 overflow-y-auto overscroll-contain rounded-lg border border-slate-100">
                    {notices.map((notice) => (
                      <li key={notice.id} className="border-b border-slate-100 last:border-0">
                        <a
                          href={notice.link || '#'}
                          className="block px-4 py-3 text-left hover:bg-slate-50"
                          onClick={closeMobileMenu}
                          target={notice.link && notice.link !== '#' ? '_blank' : undefined}
                          rel={notice.link && notice.link !== '#' ? 'noopener noreferrer' : undefined}
                        >
                          <span className="font-body font-semibold text-sm text-slate-800">{notice.title}</span>
                          {notice.description && (
                            <p className="text-xs text-slate-500 mt-1 line-clamp-2 font-body">
                              {truncate(notice.description, 100)}
                            </p>
                          )}
                        </a>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
            {user.is_authenticated && (
              <a href="/profile/" className={MOBILE_DRAWER_LINK} onClick={closeMobileMenu}>
                Profile
              </a>
            )}
          </nav>
        </aside>
        <style>{`
          @keyframes bandhu-slide-in-left {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
          }
        `}</style>
      </div>,
      document.body
    )

  return (
    <nav className="w-full bg-white">
      <div className="max-w-7xl mx-auto w-full px-3 sm:px-5 lg:px-8 py-2.5 sm:py-3">
        <div className="flex items-center gap-2 sm:gap-3 md:gap-6">
          <CurrentUpdates data={data} inline />

          <div className="hidden md:flex flex-1 min-w-0 justify-center">
            <div className="inline-flex max-w-full items-center rounded-full border border-slate-200/90 bg-white px-4 py-2">
              <div className="flex min-w-0 items-center justify-center gap-4 lg:gap-5 xl:gap-6">
                <NavLinks />
              </div>
            </div>
          </div>

          <div className="ml-auto flex shrink-0 items-center gap-2">
            <button
              type="button"
              className="md:hidden flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#005E66]/30"
              aria-expanded={mobileMenuOpen}
              aria-controls="landing-mobile-menu"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              onClick={() => (mobileMenuOpen ? closeMobileMenu() : setMobileMenuOpen(true))}
            >
              {mobileMenuOpen ? (
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
            {user.is_authenticated ? (
              <a
                href="/accounts/logout/"
                className={`${LANDING_NAVBAR_AUTH_BUTTON_CLASS} normal-case tracking-normal`}
              >
                Logout
              </a>
            ) : (
              <a
                href="#"
                className={`${LANDING_NAVBAR_AUTH_BUTTON_CLASS} normal-case tracking-normal`}
                role="button"
                data-toggle="modal"
                data-target="#loginModal"
              >
                Login
              </a>
            )}
          </div>
        </div>
      </div>
      {mobileMenuPanel}
    </nav>
  )
}
