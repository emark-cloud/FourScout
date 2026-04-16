import { Link } from 'react-router-dom'
import RiskBadge from './RiskBadge'

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

export default function TokenCard({ token }) {
  const progress = token.bonding_curve_progress || 0

  return (
    <Link
      to={`/token/${token.address}`}
      className="block bg-[var(--bg-card)] rounded-xl p-4 hover:bg-[var(--bg-hover)] no-underline border border-transparent hover:border-[var(--border)] card-hover animate-fade-in-up"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[var(--text-primary)] font-semibold">
              {token.name || 'Unknown'}
            </span>
            <span className="text-[var(--text-secondary)] text-sm">
              ${token.symbol || '???'}
            </span>
          </div>
          <div className="text-[var(--text-secondary)] text-xs mt-0.5">
            {timeAgo(token.created_at || token.launch_time)}
          </div>
        </div>
        <RiskBadge score={token.risk_score} />
      </div>

      {/* Bonding curve progress */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-[var(--text-secondary)] mb-1">
          <span>Bonding Curve</span>
          <span>{(progress * 100).toFixed(1)}%</span>
        </div>
        <div className="h-1.5 bg-[var(--bg-secondary)] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${Math.min(progress * 100, 100)}%`,
              backgroundColor: progress >= 1 ? '#0ECB81' : '#F0B90B',
            }}
          />
        </div>
      </div>

      {/* Risk rationale */}
      {token.risk_rationale && (
        <p className="text-[var(--text-secondary)] text-xs leading-relaxed line-clamp-2">
          {token.risk_rationale}
        </p>
      )}

      {/* Pending action indicator */}
      {token.pending_action && (
        <div className="mt-2 pt-2 border-t border-[var(--border)]">
          <span className="text-xs text-[var(--accent-gold)] font-medium">
            Action pending: {token.pending_action.action_type}
          </span>
        </div>
      )}
    </Link>
  )
}
