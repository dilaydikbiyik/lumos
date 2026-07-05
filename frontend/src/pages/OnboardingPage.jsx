import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LumosLogo from '../components/LumosLogo'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/clerk-react'
import DisclaimerModal from '../components/DisclaimerModal'

// 10 ateş böceği — süzülerek başlığa yaklaşır
// Her biri farklı başlangıç konumu, süre ve hareket vektörü
const FIREFLY_CONFIG = [
  { left: '8%',  top: '60%', size: '5px', dur: '3.2s', delay: '0.0s', dx: '-12px', dy: '-55px' },
  { left: '20%', top: '75%', size: '4px', dur: '2.8s', delay: '0.18s',dx: '8px',   dy: '-70px' },
  { left: '35%', top: '80%', size: '6px', dur: '3.5s', delay: '0.36s',dx: '-6px',  dy: '-65px' },
  { left: '48%', top: '70%', size: '4px', dur: '2.6s', delay: '0.54s',dx: '15px',  dy: '-60px' },
  { left: '62%', top: '78%', size: '5px', dur: '3.1s', delay: '0.72s',dx: '-10px', dy: '-72px' },
  { left: '72%', top: '65%', size: '4px', dur: '2.9s', delay: '0.90s',dx: '6px',   dy: '-58px' },
  { left: '83%', top: '72%', size: '5px', dur: '3.4s', delay: '1.08s',dx: '-14px', dy: '-68px' },
  { left: '14%', top: '55%', size: '3px', dur: '2.7s', delay: '1.26s',dx: '10px',  dy: '-48px' },
  { left: '55%', top: '85%', size: '4px', dur: '3.6s', delay: '1.44s',dx: '-8px',  dy: '-78px' },
  { left: '90%', top: '60%', size: '5px', dur: '3.0s', delay: '1.62s',dx: '-16px', dy: '-52px' },
]

const FEATURES = [
  {
    icon: '🎯',
    title: 'Seni Tanıyalım',
    desc: '7 soru, yapay zeka destekli risk profili — jargon yok, baskı yok.',
  },
  {
    icon: '📊',
    title: 'Akıllı Portföy',
    desc: 'Risk profiline göre hazırlanan kişisel yatırım planı — her kuruşun nereye gittiğini bilirsin.',
  },
  {
    icon: '🏠',
    title: 'Emlak + Borsa',
    desc: 'Küçük bütçeyle bile gayrimenkul getirisine ortak ol — iki dünya, tek çatı.',
  },
]

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [showDisclaimer, setShowDisclaimer] = useState(true)

  return (
    <div className="page">
      {/* Navbar */}
      <header className="navbar">
        <LumosLogo />
        <SignedIn><UserButton afterSignOutUrl="/" /></SignedIn>
      </header>

      <div
        className="page-content"
        style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', flex: 1 }}
      >
        {/* ── Hero Section ── */}
        <div style={{ textAlign: 'center', padding: '40px 0 48px', position: 'relative' }}>

          {/* Ateş böceği parçacıkları — başlığa süzülür */}
          <div className="fireflies" aria-hidden="true">
            {FIREFLY_CONFIG.map((ff, i) => (
              <span
                key={i}
                style={{
                  left: ff.left,
                  top: ff.top,
                  '--size':  ff.size,
                  '--dur':   ff.dur,
                  '--delay': ff.delay,
                  '--dx':    ff.dx,
                  '--dy':    ff.dy,
                }}
              />
            ))}
          </div>

          {/* Logo büyük + hero modunda */}
          <div style={{ marginBottom: 28, display: 'flex', justifyContent: 'center' }}>
            <LumosLogo size={48} hero={true} />
          </div>

          {/* Marka manifestosu */}
          <p style={{
            fontSize: 14,
            color: 'var(--text-dim)',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            fontWeight: 600,
            marginBottom: 16,
          }}>
            Yatırım karanlık bir orman gibi görünür.
          </p>

          <h1 style={{ marginBottom: 16 }}>
            Lumos,{' '}
            <span className="gradient-text">elindeki ışık.</span>
          </h1>

          <p style={{ fontSize: 15, maxWidth: 340, margin: '0 auto 32px', lineHeight: 1.7 }}>
            Yapay zeka destekli rehberle yatırım öğren, korkmadan başla,
            kendi kararını kendin ver.
          </p>

          <SignedOut>
            <SignInButton mode="modal">
              <button
                className="btn btn-primary"
                style={{ maxWidth: 320, width: '100%', margin: '0 auto', fontSize: 16, display: 'flex' }}
              >
                ✨ Başlayalım
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <button
              className="btn btn-primary"
              style={{ maxWidth: 320, width: '100%', margin: '0 auto', fontSize: 16, display: 'flex' }}
              onClick={() => navigate('/path')}
            >
              Devam Et →
            </button>
          </SignedIn>
        </div>

        {/* Glow separator */}
        <div className="glow-line" />

        {/* ── Feature Cards — Glassmorphism ── */}
        <div className="grid-3" style={{ marginBottom: 28 }}>
          {FEATURES.map((f, idx) => (
            <div
              key={f.title}
              className="card-glass"
              style={{
                textAlign: 'center',
                padding: '20px 14px',
                animationDelay: `${idx * 0.12}s`,
              }}
            >
              <div style={{
                fontSize: 28,
                marginBottom: 10,
                filter: 'drop-shadow(0 0 8px rgba(245,165,36,0.4))',
              }}>
                {f.icon}
              </div>
              <h3 style={{ fontSize: 13, marginBottom: 6, color: 'var(--text)' }}>{f.title}</h3>
              <p style={{ fontSize: 12, lineHeight: 1.55 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Dürüst beklenti cümlesi */}
        <p style={{
          textAlign: 'center', fontSize: 12, color: 'var(--text-dim)',
          lineHeight: 1.65, maxWidth: 360, margin: '0 auto 20px',
          padding: '12px 16px', borderRadius: 'var(--radius-xs)',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
        }}>
          💡 Lumos sana yol gösterir; alım-satımı kendi aracı kurumunda yaparsın,
          sonra burada takip ederiz. Hiçbir zaman senin adına işlem yapmayız.
        </p>

        {/* Disclaimer */}
        <div className="disclaimer" style={{ textAlign: 'center' }}>
          ⚠️ <strong>Yalnızca eğitim amaçlıdır.</strong> Yatırım tavsiyesi değildir.
          Lisanslı bir finansal danışmana başvurun.
        </div>
      </div>

      {showDisclaimer && <DisclaimerModal onAccept={() => setShowDisclaimer(false)} />}
    </div>
  )
}
