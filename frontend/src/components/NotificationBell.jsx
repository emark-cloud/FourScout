import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useNotifications } from './ToastNotifications'

const DOT_COLORS = {
  success: 'bg-[#0ECB81]',
  warning: 'bg-[#F0B90B]',
  error: 'bg-[#F6465D]',
  info: 'bg-[#848E9C]',
}

function timeAgo(ts) {
  const diff = Date.now() - ts
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'now'
  if (mins < 60) return `${mins}m`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h`
  return `${Math.floor(hours / 24)}d`
}

export default function NotificationBell() {
  const { history, unreadCount, markAllRead, clearHistory } = useNotifications()
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const wrapRef = useRef(null)

  useEffect(() => {
    if (!open) return
    const handler = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  const toggle = () => {
    const next = !open
    setOpen(next)
    if (next) markAllRead()
  }

  const onItemClick = (item) => {
    if (item.to) navigate(item.to)
    setOpen(false)
  }

  return (
    <div ref={wrapRef} className="relative">
      <button
        onClick={toggle}
        aria-label="Notifications"
        className="relative w-9 h-9 flex items-center justify-center rounded-lg bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
          <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-[#F6465D] text-white text-[10px] font-semibold flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg shadow-xl z-[90]">
          <div className="flex items-center justify-between px-3 py-2 border-b border-[var(--border)] sticky top-0 bg-[var(--bg-secondary)]">
            <span className="text-sm font-medium text-[var(--text-primary)]">Notifications</span>
            {history.length > 0 && (
              <button onClick={clearHistory} className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)]">
                Clear
              </button>
            )}
          </div>
          {history.length === 0 ? (
            <div className="px-4 py-6 text-center text-xs text-[var(--text-secondary)]">
              No notifications yet
            </div>
          ) : (
            <div>
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onItemClick(item)}
                  className="w-full text-left px-3 py-2 flex items-start gap-2 hover:bg-[var(--bg-card)] transition-colors border-b border-[var(--border)] last:border-b-0"
                >
                  <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${DOT_COLORS[item.type] || DOT_COLORS.info}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium text-[var(--text-primary)] truncate">{item.title}</span>
                      <span className="text-[10px] text-[var(--text-secondary)] flex-shrink-0">{timeAgo(item.createdAt)}</span>
                    </div>
                    <p className="text-xs text-[var(--text-secondary)] truncate">{item.message}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
