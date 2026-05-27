import { useEffect, useState } from 'react'

const DARK_SURFACE_SELECTORS = '#contact, .contact-footer-section, [data-cta-surface="dark"]'

/**
 * True when a dark page region (e.g. teal footer) overlaps the bottom FAB zone.
 */
export function useCtaSurfaceContrast() {
  const [onDarkSurface, setOnDarkSurface] = useState(false)

  useEffect(() => {
    const targets = document.querySelectorAll(DARK_SURFACE_SELECTORS)
    if (!targets.length) return undefined

    const visible = new Map()

    const recompute = () => {
      let onDark = false
      targets.forEach((el) => {
        if (visible.get(el)) onDark = true
      })
      setOnDarkSurface(onDark)
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          visible.set(entry.target, entry.isIntersecting && entry.intersectionRatio > 0.08)
        })
        recompute()
      },
      { rootMargin: '-72px 0px -72px 0px', threshold: [0, 0.08, 0.2, 0.5] }
    )

    targets.forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  return onDarkSurface
}
