import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

const TEAL = '#005E66'

function stripLoginModalQuery() {
  try {
    const u = new URL(window.location.href)
    if (u.searchParams.get('login_modal') !== '1') return
    u.searchParams.delete('login_modal')
    const q = u.searchParams.toString()
    const path = `${u.pathname}${q ? `?${q}` : ''}${u.hash}`
    window.history.replaceState({}, '', path)
  } catch {
    /* ignore */
  }
}

export default function LoginModal({
  open,
  onClose,
  loginUrl,
  signupUrl,
  csrfToken,
  authModal,
}) {
  const panelRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKey = (e) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  useEffect(() => {
    if (open && panelRef.current) {
      const el = panelRef.current.querySelector('input[type="email"]')
      el?.focus()
    }
  }, [open])

  if (!open) return null

  const errCode = authModal?.err_code ?? 0
  const prefill = authModal?.prefill_email ?? ''

  const handleBackdrop = (e) => {
    if (e.target === e.currentTarget) {
      stripLoginModalQuery()
      onClose()
    }
  }

  const handleCloseClick = () => {
    stripLoginModalQuery()
    onClose()
  }

  const errMsg =
    errCode === 1
      ? 'Your account has not been activated. Please activate your account to continue.'
      : errCode === 2
        ? 'Your account is not yet authorised. Kindly contact admin.'
        : errCode === 3
          ? 'Please enter the correct email and password.'
          : null

  return createPortal(
    <div
      className="fixed inset-0 z-[300] flex items-center justify-center p-4 bg-black/45 backdrop-blur-[2px]"
      role="presentation"
      onMouseDown={handleBackdrop}
    >
      <div
        ref={panelRef}
        className="relative w-full max-w-md rounded-2xl bg-white shadow-2xl ring-1 ring-black/10 overflow-hidden max-h-[90vh] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-labelledby="login-modal-title"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 pt-4 pb-2 border-b border-black/[0.06]">
          <h2 id="login-modal-title" className="font-heading text-lg font-bold text-slate-800">
            Sign In
          </h2>
          <button
            type="button"
            onClick={handleCloseClick}
            className="rounded-full p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition-colors"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-5 py-5">
          <div className="flex gap-2 mb-4">
            <a
              href="/oauth/login/facebook/"
              className="flex-1 flex items-center justify-center gap-2 rounded-full py-2.5 px-4 text-base font-heading font-bold text-white bg-[#1877f2] hover:bg-[#166fe5] transition-colors"
            >
              <span className="text-lg leading-none" aria-hidden>
                f
              </span>
              Facebook
            </a>
            <a
              href="/oauth/login/google-oauth2/"
              className="flex-1 flex items-center justify-center gap-2 rounded-full border-2 border-slate-200 bg-white py-2.5 px-4 text-base font-heading font-bold text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" aria-hidden>
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Google
            </a>
          </div>

          <p className="text-center text-xs text-slate-500 mb-1">— OR —</p>
          <p className="text-center text-sm text-slate-600 mb-3">Sign in using email</p>

          {errMsg && (
            <p className="text-sm text-red-600 text-center mb-3 px-1" role="alert">
              {errMsg}
            </p>
          )}

          <form method="post" action={loginUrl} className="space-y-3">
            <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken || ''} />
            <input type="hidden" name="login_modal" value="1" />
            <input type="hidden" name="next" value="/" />
            <input
              name="email"
              type="email"
              required
              autoComplete="username"
              placeholder="Email"
              defaultValue={prefill}
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#005E66]/30 focus:border-[#005E66]"
            />
            <input
              name="password"
              type="password"
              required
              autoComplete="current-password"
              placeholder="Password"
              className="w-full rounded-lg border border-slate-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#005E66]/30 focus:border-[#005E66]"
            />
            <div className="text-right">
              <a href="/accounts/password_reset/" className="text-sm font-semibold hover:underline" style={{ color: TEAL }}>
                Forgot password?
              </a>
            </div>
            <button type="submit" className={`${CTA_PILL_CLASS} w-full justify-center`}>
              Sign In
            </button>
          </form>

          <p className="text-center text-sm text-slate-600 mt-4">
            Not a member?{' '}
            <a href={signupUrl} className="font-bold hover:underline" style={{ color: TEAL }}>
              Sign up now
            </a>
          </p>
        </div>
      </div>
    </div>,
    document.body
  )
}
