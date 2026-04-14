import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getPositions } from '../services/api'

export default function Positions() {
  const [positions, setPositions] = useState([])
  const [filter, setFilter] = useState('active')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getPositions(filter)
        setPositions(data)
      } catch (e) {
        console.error('Positions load error:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [filter])

  const pnlColor = (pnl) => {
    if (!pnl) return 'text-[var(--text-secondary)]'
    return pnl > 0 ? 'text-[#0ECB81]' : 'text-[#F6465D]'
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-[var(--text-primary)]">Positions</h1>
        <div className="flex gap-2">
          {['active', 'closed', 'all'].map((f) => (
            <button
              key={f}
              onClick={() => { setFilter(f); setLoading(true) }}
              className={`px-3 py-1 rounded text-sm cursor-pointer capitalize ${
                filter === f
                  ? 'bg-[var(--accent-gold)] text-black'
                  : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">Loading...</div>
      ) : positions.length === 0 ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">
          No {filter} positions yet
        </div>
      ) : (
        <div className="bg-[var(--bg-card)] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-[var(--text-secondary)] border-b border-[var(--border)]">
                <th className="text-left px-4 py-3 font-medium">Token</th>
                <th className="text-right px-4 py-3 font-medium">Entry</th>
                <th className="text-right px-4 py-3 font-medium">Current</th>
                <th className="text-right px-4 py-3 font-medium">Amount</th>
                <th className="text-right px-4 py-3 font-medium">PnL</th>
                <th className="text-right px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => (
                <tr key={pos.id} className="border-b border-[var(--border)] hover:bg-[var(--bg-hover)]">
                  <td className="px-4 py-3">
                    <Link to={`/token/${pos.token_address}`} className="text-[var(--accent-gold)] no-underline font-mono text-xs">
                      {pos.token_address.slice(0, 10)}...
                    </Link>
                  </td>
                  <td className="text-right px-4 py-3 text-[var(--text-primary)]">
                    {pos.entry_price?.toFixed(8) || '-'}
                  </td>
                  <td className="text-right px-4 py-3 text-[var(--text-primary)]">
                    {pos.current_price?.toFixed(8) || '-'}
                  </td>
                  <td className="text-right px-4 py-3 text-[var(--text-primary)]">
                    {pos.entry_amount_bnb?.toFixed(4) || '-'} BNB
                  </td>
                  <td className={`text-right px-4 py-3 font-medium ${pnlColor(pos.pnl_bnb)}`}>
                    {pos.pnl_bnb != null ? `${pos.pnl_bnb > 0 ? '+' : ''}${pos.pnl_bnb.toFixed(4)} BNB` : '-'}
                  </td>
                  <td className="text-right px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded capitalize ${
                      pos.status === 'active' ? 'bg-[rgba(14,203,129,0.15)] text-[#0ECB81]' : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)]'
                    }`}>
                      {pos.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
