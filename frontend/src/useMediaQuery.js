import { useEffect, useState } from 'react'

/** Subscribe to a CSS media query; `defaultMatches` is used until mount (SSR-safe). */
export function useMediaQuery(query, defaultMatches = false) {
  const [matches, setMatches] = useState(defaultMatches)

  useEffect(() => {
    const mq = window.matchMedia(query)
    const onChange = () => setMatches(mq.matches)
    onChange()
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [query])

  return matches
}
