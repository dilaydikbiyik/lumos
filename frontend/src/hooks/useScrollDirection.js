import { useEffect, useState } from 'react'

/**
 * True while the user is scrolling DOWN (reading). Floating buttons use this
 * to get out of the way of the content — they slide back in the moment the
 * user scrolls up or stops, so a crisis-moment button is never far away.
 */
export default function useScrollDirection() {
  const [hidden, setHidden] = useState(false)

  useEffect(() => {
    let lastY = window.scrollY
    let idleTimer = null

    const onScroll = () => {
      const y = window.scrollY
      // Ignore rubber-banding and micro-scrolls
      if (Math.abs(y - lastY) < 8) return
      setHidden(y > lastY && y > 120)
      lastY = y
      clearTimeout(idleTimer)
      idleTimer = setTimeout(() => setHidden(false), 900)  // reappear when idle
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      clearTimeout(idleTimer)
    }
  }, [])

  return hidden
}
