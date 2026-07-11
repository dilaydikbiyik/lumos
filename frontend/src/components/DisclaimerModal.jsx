import { useState } from 'react'

export default function DisclaimerModal({ onAccept }) {
  const [checked, setChecked] = useState(false)

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: 16,
    }}>
      <div className="card" style={{ maxWidth: 480, width: '100%' }}>
        <div style={{ fontSize: 36, marginBottom: 16, textAlign: 'center' }}>⚠️</div>
        <h2 style={{ marginBottom: 12, textAlign: 'center' }}>Önemli Uyarı</h2>

        <p style={{ fontSize: 14, marginBottom: 16, lineHeight: 1.7 }}>
          <strong style={{ color: 'var(--text)' }}>Lumos yalnızca bir eğitim aracıdır.</strong><br />
          Yatırım tavsiyesi, finansal planlama veya düzenlemeye tabi finansal hizmet <em>vermez</em>.
        </p>

        <div className="disclaimer" style={{ marginBottom: 20 }}>
          Bu uygulamanın ürettiği portföy önerileri, halka açık piyasa verilerine ve yapay
          zeka analizine dayanır. Hiçbir yatırım kararının <strong>tek dayanağı</strong> olmamalıdır.
          Yatırım yapmadan önce mutlaka lisanslı bir finansal danışmana başvurun.
        </div>

        <label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', cursor: 'pointer', marginBottom: 20, fontSize: 14, color: 'var(--text-muted)' }}>
          <input
            type="checkbox"
            checked={checked}
            onChange={e => setChecked(e.target.checked)}
            style={{ marginTop: 2, accentColor: 'var(--accent)', width: 16, height: 16 }}
          />
          Bu uygulamanın yalnızca eğitim amaçlı olduğunu ve yatırım tavsiyesi niteliği taşımadığını anlıyorum.
        </label>

        <button
          className="btn btn-primary"
          style={{ width: '100%', justifyContent: 'center' }}
          disabled={!checked}
          onClick={onAccept}
        >
          Lumos'a Devam Et →
        </button>
      </div>
    </div>
  )
}
