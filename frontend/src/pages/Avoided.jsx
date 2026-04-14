import { useState, useEffect } from 'react'
import RiskBadge from '../components/RiskBadge'
import { getAvoided, getAvoidedStats } from '../services/api'

export default function Avoided() {
  const [avoided, setAvoided] = useState([])
  const [stats, setStats] = useState({ total_flagged: 0, confirmed_rugs: 0, estimated_savings_bnb: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [avoidedData, statsData] = await Promise.all([
          getAvoided(),
          getAvoidedStats(),
        ])
        setAvoided(avoidedData)
        setStats(statsData)
      } catch (e) {
        console.error('Avoided load error:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div>
      <h1 className="text-xl font-bold text-[var(--text-primary)] mb-2">What I Avoided</h1>
      <p className="text-sm text-[var(--text-secondary)] mb-6">
        Tokens the agent flagged as dangerous, tracked over time
      </p>

      {/* Stats banner */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-[var(--bg-card)] rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[var(--text-primary)]">{stats.total_flagged}</div>
          <div className="text-xs text-[var(--text-secondary)]">Tokens Flagged</div>
        </div>
        <div className="bg-[var(--bg-card)] rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[#F6465D]">{stats.confirmed_rugs}</div>
          <div className="text-xs text-[var(--text-secondary)]">Confirmed Rugs</div>
        </div>
        <div className="bg-[var(--bg-card)] rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-[#0ECB81]">{stats.estimated_savings_bnb.toFixed(3)} BNB</div>
          <div className="text-xs text-[var(--text-secondary)]">Estimated Savings</div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">Loading...</div>
      ) : avoided.length === 0 ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">
          No tokens flagged yet. The agent is scanning...
        </div>
      ) : (
        <div className="space-y-3">
          {avoided.map((item) => {
            const priceNow = item.price_24h_later || item.price_6h_later || item.price_1h_later
            const priceDrop = priceNow && item.price_at_flag
              ? ((priceNow - item.price_at_flag) / item.price_at_flag * 100).toFixed(1)
              : null

            return (
              <div key={item.id} className="bg-[var(--bg-card)] rounded-xl p-4 flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-[var(--text-primary)]">{item.token_name || 'Unknown'}</span>
                    <RiskBadge score={item.risk_score} />
                    {item.confirmed_rug ? (
                      <span className="text-xs px-2 py-0.5 rounded bg-[rgba(246,70,93,0.15)] text-[#F6465D] font-medium">
                        CONFIRMED RUG
                      </span>
                    ) : null}
                  </div>
                  <p className="text-xs text-[var(--text-secondary)]">{item.risk_rationale}</p>
                </div>
                <div className="text-right">
                  {priceDrop !== null && (
                    <div className={`text-lg font-bold ${parseFloat(priceDrop) < 0 ? 'text-[#F6465D]' : 'text-[#0ECB81]'}`}>
                      {priceDrop}%
                    </div>
                  )}
                  {item.estimated_savings_bnb > 0 && (
                    <div className="text-xs text-[#0ECB81]">
                      Saved {item.estimated_savings_bnb.toFixed(3)} BNB
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
