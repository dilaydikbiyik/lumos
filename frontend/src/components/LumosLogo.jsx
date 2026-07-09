import { useNavigate } from 'react-router-dom'

/**
 * Lumos marka logosu — ateş böceği animasyonu + ışıldayan yazı.
 * CSS class'ları: lumos-brand, lumos-wordmark, lumos-firefly
 * "Karanlıkta yol gösteren minik ışık" — marka hikayesinin kendisi.
 */

// 4 ateş böceğinin konumu ve hareket parametreleri
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
      {/* Ateşböceği ikonu — şeffaf SVG, arka plan yok */}
      <img
        src="/logo-icon.svg"
        alt=""
        width={size * 1.4}
        height={size * 1.4}
        style={{
          filter: 'drop-shadow(0 0 5px rgba(245,165,36,0.55))',
          flexShrink: 0,
        }}
      />

      {/* Yazı + uçuşan ateş böcekleri */}
      <div className={`lumos-brand${hero ? ' lumos-brand--hero' : ''}`}>
        <span
          className="lumos-wordmark"
          style={{ fontSize: size * 0.85, lineHeight: 1 }}
        >
          Lumos
        </span>

        {/* 4 uçuşan ateş böceği — yazının üzerinde dolaşır */}
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
