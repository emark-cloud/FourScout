const RISK_STYLES = {
  green: {
    bg: 'bg-[rgba(14,203,129,0.15)]',
    text: 'text-[#0ECB81]',
    border: 'border-[#0ECB81]',
    dot: 'bg-[#0ECB81]',
    label: 'Low Risk',
  },
  amber: {
    bg: 'bg-[rgba(240,185,11,0.15)]',
    text: 'text-[#F0B90B]',
    border: 'border-[#F0B90B]',
    dot: 'bg-[#F0B90B]',
    label: 'Moderate',
  },
  red: {
    bg: 'bg-[rgba(246,70,93,0.15)]',
    text: 'text-[#F6465D]',
    border: 'border-[#F6465D]',
    dot: 'bg-[#F6465D]',
    label: 'High Risk',
  },
}

export default function RiskBadge({ score, size = 'sm' }) {
  const style = RISK_STYLES[score] || RISK_STYLES.amber

  if (size === 'lg') {
    return (
      <span
        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${style.bg} ${style.text} ${style.border} text-sm font-medium`}
      >
        <span className={`w-2.5 h-2.5 rounded-full ${style.dot}`} />
        {style.label}
      </span>
    )
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full ${style.bg} ${style.text} text-xs font-medium`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
      {style.label}
    </span>
  )
}
