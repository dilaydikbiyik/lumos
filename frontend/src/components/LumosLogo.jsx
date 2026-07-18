import { useNavigate } from 'react-router-dom'
import FireflyMark from './FireflyMark'

/**
 * Lumos brand logo — firefly animation + glowing wordmark.
 * CSS classes: lumos-brand, lumos-wordmark, lumos-firefly
 * "A tiny light guiding through the dark" — the brand story itself.
 */

// Position and motion parameters for the 4 fireflies
const FIREFLIES = [
  { left: '5%',   top: '-85%', dur: '6.5s', delay: '0s',    dx: '16px',  dy: '-12px' },
  { left: '28%',  top: '-70%', dur: '8s',   delay: '0.9s',  dx: '-14px', dy: '-18px' },
  { left: '58%',  top: '-90%', dur: '7s',   delay: '0.4s',  dx: '18px',  dy: '-10px' },
  { left: '82%',  top: '-75%', dur: '9s',   delay: '1.5s',  dx: '-10px', dy: '-20px' },
]

export default function LumosLogo({ size = 22, hero = false }) {
  const navigate = useNavigate()

  return (
    <button
      onClick={() => navigate('/')}
      aria-label="Lumos anasayfa"
      style={{
        display: 'flex', alignItems: 'center', gap: 8,
        background: 'none', border: 'none', cursor: 'pointer', padding: '4px 0',
      }}
    >
      {/* Firefly icon — alignItems:center puts icon mid-point at div mid-point.
          A small marginTop nudges the icon down to the cap-height centre of "L"
          (the wordmark div is taller than one line because it holds firefly
          particles with absolute positioning above the text). */}
      <FireflyMark
        size={size * 1.4}
        style={{
          filter: 'drop-shadow(0 0 5px rgba(245,165,36,0.55))',
          marginTop: '0.55em',
        }}
      />

      {/* Wordmark + roaming fireflies */}
      <div className={`lumos-brand${hero ? ' lumos-brand--hero' : ''}`}>
        <span
          className="lumos-wordmark"
          style={{ fontSize: size * 0.85, lineHeight: 1 }}
        >
          Lumos
        </span>

        {/* 4 roaming fireflies — drift above the wordmark */}
        {FIREFLIES.map((ff, i) => (
          <span
            key={i}
            className="lumos-firefly"
            style={{
              left: ff.left,
              top: ff.top,
              '--dur': ff.dur,
              '--delay': ff.delay,
              '--dx': ff.dx,
              '--dy': ff.dy,
            }}
            aria-hidden="true"
          />
        ))}
      </div>
    </button>
  )
}
