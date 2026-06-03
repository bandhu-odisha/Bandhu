import { createPortal } from 'react-dom'
import { useCtaSurfaceContrast } from '../useCtaSurfaceContrast'
import { ctaPillClass } from '../cta'

export default function BeABandhuFab({ className = '' }) {
  const onDarkSurface = useCtaSurfaceContrast()

  const fab = (
    <div
      className="fixed z-[185] bottom-0 left-0 right-0 flex justify-center px-4 pb-4 pointer-events-none sm:left-auto sm:right-7 sm:bottom-7 sm:block sm:px-0 sm:pb-0"
      style={{ paddingBottom: 'max(1rem, env(safe-area-inset-bottom, 0px))' }}
    >
      <button
        type="button"
        className={`auth-open-signup-modal pointer-events-auto touch-manipulation max-sm:w-full max-sm:max-w-sm max-sm:justify-center ${ctaPillClass(onDarkSurface)} ${className}`.trim()}
        aria-label="Be a Bandhu — sign up"
      >
        Be a Bandhu
      </button>
    </div>
  )

  if (typeof document === 'undefined') return fab
  return createPortal(fab, document.body)
}
