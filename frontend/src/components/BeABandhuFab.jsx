import { useCtaSurfaceContrast } from '../useCtaSurfaceContrast'
import { ctaPillClass } from '../cta'

export default function BeABandhuFab({ href, className = '' }) {
  const onDarkSurface = useCtaSurfaceContrast()

  return (
    <a
      href={href}
      className={`fixed bottom-5 right-5 z-[160] sm:bottom-7 sm:right-7 ${ctaPillClass(onDarkSurface)} ${className}`.trim()}
      style={{ marginBottom: 'max(0.25rem, env(safe-area-inset-bottom, 0px))' }}
      aria-label="Be a Bandhu — sign up"
    >
      Be a Bandhu
    </a>
  )
}
