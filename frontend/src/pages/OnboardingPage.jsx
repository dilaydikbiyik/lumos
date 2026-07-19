import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@clerk/clerk-react'
import api from '../utils/api'
import LumosLogo from '../components/LumosLogo'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/clerk-react'
import DisclaimerModal from '../components/DisclaimerModal'
import Icon from '../components/Icon'
import { isInAppBrowser } from '../utils/inAppBrowser'

// 10 fireflies — drift toward the title
// Each with its own start position, duration and motion vector
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
    icon: 'trendUp',
    title: 'Enflasyon Sonrası Gerçek Getiri',
    desc: '"%300 kazandım" demek, enflasyon %320\'yse kaybettin demektir. Lumos her rakamı TCMB verisiyle enflasyondan arındırıp gösterir.',
  },
  {
    icon: 'home',
    title: 'Emlak ve Borsa Yan Yana',
    desc: '81 ilin m² fiyatı ve gerçek değerlenmesi, hisse portföyünle aynı ekranda. Kirada mı otur, ev mi al — hesabı burada.',
  },
  {
    icon: 'lifebuoy',
    title: 'Panik Anında Yanında',
    desc: 'En pahalı hata, düşüşte satmaktır. Piyasa çakıldığında tek dokunuşla veriye dayalı, sakin bir ses.',
  },
]

export default function OnboardingPage() {
  const navigate = useNavigate()
  const { userId } = useAuth()

  // A returning user with a finished risk profile must not walk the
  // 3-step intro (path → fear check-in → quiz) again: straight to the
  // dashboard. Cache answers instantly; the server confirms in the rare
  // cache-miss case.
  async function continueFromHero() {
    if (userId && localStorage.getItem(`lumos-profile-${userId}`)) {
      navigate('/dashboard')
      return
    }
    try {
      const res = await api.get('/profile')
      if (res.data?.risk_score != null) {
        navigate('/dashboard')
        return
      }
    } catch { /* can't tell — fall through to the intro */ }
    navigate('/path')
  }
  // Accepted once per device — re-prompting on every visit numbs the warning
  const [showDisclaimer, setShowDisclaimer] = useState(
    () => localStorage.getItem('lumos-disclaimer-ok') !== '1',
  )
  const acceptDisclaimer = () => {
    localStorage.setItem('lumos-disclaimer-ok', '1')
    setShowDisclaimer(false)
  }

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

          {/* Firefly particles — drift toward the title */}
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

          {/* Logo large + in hero mode */}
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

          <p style={{ fontSize: 'var(--t-body)', maxWidth: 360, margin: '0 auto 20px', lineHeight: 1.7 }}>
            Yatırımı korkmadan öğren: her rakam enflasyondan arındırılmış,
            her öneri adım adım açıklanmış, kararın her zaman sende.
          </p>

          {/* Trust strip — the concrete, checkable claims behind the promise */}
          <div style={{
            display: 'flex', flexWrap: 'wrap', gap: '6px 10px', justifyContent: 'center',
            maxWidth: 380, margin: '0 auto 32px',
          }}>
            {['TCMB resmî verisi', '81 il emlak endeksi', 'Gerçek piyasa fiyatları', 'Formülü görünür'].map(t => (
              <span key={t} style={{
                fontSize: 'var(--t-micro)', color: 'var(--text-muted)',
                border: '1px solid var(--border)', borderRadius: 999,
                padding: '4px 10px', background: 'var(--bg-card)',
              }}>{t}</span>
            ))}
          </div>

          <SignedOut>
            {isInAppBrowser() && (
              <div style={{
                maxWidth: 320, margin: '0 auto 12px', padding: '10px 14px',
                borderRadius: 'var(--radius-xs)', border: '1px solid var(--border)',
                background: 'var(--bg-input)', fontSize: 12.5, lineHeight: 1.6,
                color: 'var(--text-muted)', textAlign: 'left',
              }}>
                Bu sayfayı uygulama içi tarayıcıda açtın. Google ile giriş burada
                çalışmıyor — sağ üstteki menüden <strong>&quot;Tarayıcıda aç&quot;</strong>{' '}
                dersen sorunsuz giriş yapabilirsin.
              </div>
            )}
            <SignInButton mode="modal">
              <button
                className="btn btn-primary"
                style={{ maxWidth: 320, width: '100%', margin: '0 auto', fontSize: 16, display: 'flex' }}
              >
                Başlayalım
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <button
              className="btn btn-primary"
              style={{ maxWidth: 320, width: '100%', margin: '0 auto', fontSize: 16, display: 'flex' }}
              onClick={continueFromHero}
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
              <div style={{ marginBottom: 10 }}>
                <Icon name={f.icon} size={28} glow />
              </div>
              <h3 style={{ fontSize: 'var(--t-body)', marginBottom: 6, color: 'var(--text)' }}>{f.title}</h3>
              <p style={{ fontSize: 'var(--t-small)', lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Honest expectation line */}
        <p style={{
          textAlign: 'center', fontSize: 12, color: 'var(--text-dim)',
          lineHeight: 1.65, maxWidth: 360, margin: '0 auto 20px',
          padding: '12px 16px', borderRadius: 'var(--radius-xs)',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
        }}>
          <Icon name="bulb" size={14} /> Lumos sana yol gösterir; alım-satımı kendi aracı kurumunda yaparsın,
          sonra burada takip ederiz. Hiçbir zaman senin adına işlem yapmayız.
        </p>

        {/* Disclaimer */}
        <div className="disclaimer" style={{ textAlign: 'center' }}>
          <Icon name="warning" size={14} /> <strong>Yalnızca eğitim amaçlıdır.</strong> Yatırım tavsiyesi değildir.
          Lisanslı bir finansal danışmana başvurun.
        </div>
      </div>

      {showDisclaimer && <DisclaimerModal onAccept={acceptDisclaimer} />}
    </div>
  )
}
