import { useState, useEffect } from 'react'
import { getActivity } from '../services/api'

const EVENT_ICONS = {
  approve: { icon: '\u{2705}', label: 'Approved' },
  reject: { icon: '\u{274C}', label: 'Rejected' },
  trade_executed: { icon: '\u{1F4B0}', label: 'Trade Executed' },
  avoided_confirmed: { icon: '\u{1F6E1}', label: 'Rug Confirmed' },
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function Activity() {
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const data = await getActivity(100)
        setActivity(data)
      } catch (e) {
        console.error('Activity load error:', e)
      } finally {
        setLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 className="text-xl font-bold text-[var(--text-primary)] mb-6">Activity Feed</h1>

      {loading ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">Loading...</div>
      ) : activity.length === 0 ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">No activity yet</div>
      ) : (
        <div className="space-y-2">
          {activity.map((item) => {
            const event = EVENT_ICONS[item.event_type] || { icon: '\u{25CF}', label: item.event_type }
            let detail = {}
            try { detail = item.detail ? JSON.parse(item.detail) : {} } catch { /* ignore */ }

            return (
              <div key={item.id} className="bg-[var(--bg-card)] rounded-lg px-4 py-3 flex items-center gap-3">
                <span className="text-lg">{event.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-[var(--text-primary)]">{event.label}</span>
                    {item.token_address && (
                      <span className="text-xs font-mono text-[var(--text-secondary)]">
                        {item.token_address.slice(0, 10)}...
                      </span>
                    )}
                  </div>
                  {(detail.side || detail.tx_hash) && (
                    <p className="text-xs text-[var(--text-secondary)]">
                      {detail.side === 'buy' && `Buy ${detail.amount_bnb} BNB `}
                      {detail.side === 'sell' && `Sell · PnL ${detail.pnl_bnb > 0 ? '+' : ''}${detail.pnl_bnb} BNB `}
                      {detail.tx_hash && (
                        <a
                          href={`https://bscscan.com/tx/${detail.tx_hash}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[var(--accent-gold)] ml-1"
                        >
                          View TX
                        </a>
                      )}
                    </p>
                  )}
                </div>
                <span className="text-xs text-[var(--text-secondary)] whitespace-nowrap">
                  {timeAgo(item.created_at)}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
