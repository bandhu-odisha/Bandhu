import { createPortal } from 'react-dom'
import { useCtaSurfaceContrast } from '../useCtaSurfaceContrast'
import { ctaFabPillClass } from '../cta'

export default function BeABandhuFab({ className = '' }) {
  const onDarkSurface = useCtaSurfaceContrast()

  const fab = (
    <div
      className="fixed z-[185] pointer-events-none"
      style={{ right: '16px', bottom: 'max(16px, env(safe-area-inset-bottom, 0px))' }}
    >
      <button
        type="button"
        className={`auth-open-signup-modal pointer-events-auto touch-manipulation ${ctaFabPillClass(onDarkSurface)} ${className}`.trim()}
        aria-label="Be a Bandhu — sign up"
      >
        <i className="fas fa-handshake text-[0.95em] max-sm:text-xl leading-none" aria-hidden="true" />
        <span className="max-sm:text-[11px] max-sm:leading-tight max-sm:whitespace-nowrap" aria-hidden="true">
          Be a <strong lang="or" className="font-bold">ବନ୍ଧୁ</strong>
        </span>
      </button>
    </div>
  )

  if (typeof document === 'undefined') return fab
  return createPortal(fab, document.body)
}
