import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@clerk/clerk-react'
import api, { setAuthToken } from '../utils/api'

/**
 * Gerçek portföy vs önerilen portföy karşılaştırması.
 * Hedef dağılımdan sapmaları gösterir + kısa aksiyon önerisi.
 */

const CATEGORY_LABELS = {
  stock: 'Hisse', fund: 'Fon', etf: 'ETF',
  real_estate: 'Emlak', land: 'Arsa', vehicle: 'Araç',
  gold: 'Altın', crypto: 'Kripto', cash: 'Nakit', other: 'Diğer',
}

const CATEGORY_COLORS = {
  stock: 'var(--firefly)', fund: 'var(--accent)', etf: 'var(--accent-2)',
  real_estate: 'var(--green)', land: '#8B7355', gold: '#FFD700',
  crypto: '#9B59B6', cash: 'var(--text-dim)', vehicle: 'var(--red)', other: '#666',
}


export default function PortfolioComparison() {
  const { getToken } = useAuth()
  const [data, setData] = useState(null)

  const load = useCallback(async () => {
    try {
      setAuthToken(await getToken())
      const [summaryRes, profileRes] = await Promise.all([
        api.get('/holdings/summary'),
        api.get('/profile'),
      ])

      const summary = summaryRes.data
      const profile = profileRes.data

      // Gerçek dağılım (holdings/summary → by_type)
      if (!summary?.by_type || !profile?.risk_score) return

      const totalValue = summary.total_current_value || 0
      if (totalValue === 0) return

      const actual = {}
      Object.entries(summary.by_type).forEach(([type, val]) => {
        actual[type] = (val.current_value / totalValue) * 100
      })

      // Basit hedef dağılım (risk skoruna göre)
      const riskScore = profile.risk_score
      const target = generateTargetAllocation(riskScore)

      // Sapma hesapla
      const allTypes = new Set([...Object.keys(actual), ...Object.keys(target)])
      const comparison = []
      allTypes.forEach(type => {
        const actualPct = actual[type] || 0
        const targetPct = target[type] || 0
        const deviation = actualPct - targetPct
        if (actualPct > 0 || targetPct > 0) {
          comparison.push({
            type,
            label: CATEGORY_LABELS[type] || type,
            color: CATEGORY_COLORS[type] || 'var(--text-dim)',
            actual: Math.round(actualPct),
            target: Math.round(targetPct),
            deviation: Math.round(deviation),
          })
        }
      })

      comparison.sort((a, b) => Math.abs(b.deviation) - Math.abs(a.deviation))
      setData({ comparison, riskScore })
    } catch {
      // Karşılaştırma kritik değil
    }
  }, [getToken])

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { load() }, [load])

  if (!data || data.comparison.length === 0) return null

  const maxDeviation = Math.max(...data.comparison.map(c => Math.abs(c.deviation)))
  const isBalanced = maxDeviation <= 10

  return (
    <div className="card" style={{
      border: isBalanced ? '1px solid rgba(61,214,140,0.2)' : '1px solid rgba(245,165,36,0.2)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>{isBalanced ? '✅' : '⚖️'}</span>
        <div>
          <h3 style={{ fontSize: 14, fontWeight: 700 }}>
            {isBalanced ? 'Portföyün Dengede' : 'Hedef Dağılımdan Sapmalar'}
          </h3>
          <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>
            Risk {data.riskScore}/10 profiline göre önerilen vs gerçek dağılım
          </p>
        </div>
      </div>

      {/* Karşılaştırma bar'ları */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {data.comparison.map(item => (
          <div key={item.type}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ fontSize: 12, fontWeight: 500 }}>
                <span style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: item.color, display: 'inline-block',
                  marginRight: 6, verticalAlign: 'middle',
                }} />
                {item.label}
              </span>
              <span style={{
                fontSize: 11, fontWeight: 600,
                color: item.deviation === 0 ? 'var(--text-dim)'
                  : item.deviation > 0 ? 'var(--firefly)'
                  : 'var(--accent-2)',
              }}>
                {item.deviation > 0 ? '+' : ''}{item.deviation}%
              </span>
            </div>
            {/* Çift bar: üstte gerçek, altta hedef */}
            <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
              <span style={{ fontSize: 10, color: 'var(--text-dim)', width: 32 }}>%{item.actual}</span>
              <div style={{ flex: 1, height: 6, background: 'var(--bg)', borderRadius: 3, overflow: 'hidden' }}>
                <div style={{
                  width: `${Math.min(item.actual, 100)}%`,
                  height: '100%', borderRadius: 3,
                  background: item.color,
                  transition: 'width 0.6s ease',
                }} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 4, alignItems: 'center', marginTop: 2 }}>
              <span style={{ fontSize: 10, color: 'var(--text-dim)', width: 32 }}>%{item.target}</span>
              <div style={{ flex: 1, height: 4, background: 'var(--bg)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{
                  width: `${Math.min(item.target, 100)}%`,
                  height: '100%', borderRadius: 2,
                  background: `${item.color}55`,
                  transition: 'width 0.6s ease',
                  borderTop: '1px dashed var(--border)',
                }} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Lejant */}
      <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 10, color: 'var(--text-dim)' }}>
        <span>■ Gerçek dağılım</span>
        <span style={{ opacity: 0.5 }}>■ Hedef dağılım</span>
      </div>
    </div>
  )
}

/**
 * Risk skoruna göre basit hedef dağılım üret.
 * Düşük risk → daha çok altın/nakit, yüksek risk → daha çok hisse.
 */
function generateTargetAllocation(riskScore) {
  if (riskScore <= 3) {
    return { gold: 30, fund: 25, etf: 15, cash: 20, stock: 10 }
  } else if (riskScore <= 5) {
    return { stock: 20, fund: 25, etf: 20, gold: 20, cash: 15 }
  } else if (riskScore <= 7) {
    return { stock: 35, etf: 25, fund: 15, gold: 15, cash: 10 }
  } else {
    return { stock: 45, etf: 25, fund: 10, gold: 10, cash: 10 }
  }
}
