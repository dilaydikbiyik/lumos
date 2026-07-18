import { useId } from 'react'

/**
 * The firefly brand mark, inline.
 *
 * It used to be <img src="/favicon.svg">, which loads asynchronously — on
 * every route change the header remounted and the logo blinked out for a
 * frame before the image resolved. Inline SVG renders synchronously, so the
 * mark is simply always there. useId() keeps gradient/filter ids unique when
 * several marks are on screen (header + sidebar).
 */
export default function FireflyMark({ size = 30, style }) {
  const uid = useId().replace(/:/g, '')
  const body = `body-${uid}`
  const glow = `glow-${uid}`
  const wing = `wing-${uid}`

  return (
    <svg
      width={size} height={size} viewBox="0 0 120 120" fill="none"
      aria-hidden="true" style={{ flexShrink: 0, ...style }}
    >
      <defs>
        <linearGradient id={body} x1="60" y1="28" x2="60" y2="88" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FFB300" />
          <stop offset="45%" stopColor="#FF8C00" />
          <stop offset="100%" stopColor="#E64A00" />
        </linearGradient>
        <filter id={glow} x="-60%" y="-60%" width="220%" height="220%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id={wing} x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="2.5" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <path d="M60 52 C50 38, 24 32, 26 52 C27 62, 42 70, 56 66"
        stroke="#C8A84B" strokeWidth="1.8" strokeLinecap="round" fill="none"
        filter={`url(#${wing})`} opacity="0.85" />
      <path d="M60 58 C54 46, 34 40, 34 56 C34 64, 44 69, 56 67"
        stroke="#C8A84B" strokeWidth="1.2" strokeLinecap="round" fill="none" opacity="0.55" />
      <path d="M60 52 C70 38, 96 32, 94 52 C93 62, 78 70, 64 66"
        stroke="#C8A84B" strokeWidth="1.8" strokeLinecap="round" fill="none"
        filter={`url(#${wing})`} opacity="0.85" />
      <path d="M60 58 C66 46, 86 40, 86 56 C86 64, 76 69, 64 67"
        stroke="#C8A84B" strokeWidth="1.2" strokeLinecap="round" fill="none" opacity="0.55" />

      <path d="M60 28 C60 28, 64 38, 64 54 C64 68, 62 80, 60 88 C58 80, 56 68, 56 54 C56 38, 60 28, 60 28 Z"
        fill={`url(#${body})`} filter={`url(#${glow})`} />
      <circle cx="60" cy="27" r="5" fill="#FFD740" filter={`url(#${glow})`} />
      <circle cx="60" cy="60" r="3.2" fill="white" opacity="0.92" filter={`url(#${glow})`} />
      <ellipse cx="60" cy="60" rx="10" ry="28" fill="#FF8C00" opacity="0.07" />
    </svg>
  )
}
