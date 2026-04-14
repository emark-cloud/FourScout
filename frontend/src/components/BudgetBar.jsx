export default function BudgetBar({ used = 0, max = 0.3, trades = 0, positions = 0 }) {
  const pct = max > 0 ? Math.min((used / max) * 100, 100) : 0
  const color = pct > 80 ? '#F6465D' : pct > 50 ? '#F0B90B' : '#0ECB81'

  return (
    <div className="bg-[var(--bg-card)] rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-[var(--text-secondary)]">Daily Budget</span>
        <span className="text-sm font-medium" style={{ color }}>
          {used.toFixed(3)} / {max} BNB
        </span>
      </div>
      <div className="h-2 bg-[var(--bg-secondary)] rounded-full overflow-hidden mb-3">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <div className="flex gap-4 text-xs text-[var(--text-secondary)]">
        <span>Trades today: <strong className="text-[var(--text-primary)]">{trades}</strong></span>
        <span>Active positions: <strong className="text-[var(--text-primary)]">{positions}</strong></span>
      </div>
    </div>
  )
}
