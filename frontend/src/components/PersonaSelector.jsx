const PERSONAS = [
  {
    id: 'conservative',
    name: 'Conservative',
    icon: '\u{1F6E1}',
    color: '#0ECB81',
    desc: 'Low frequency, strong confirmation required. Avoids tokens under 10 min old.',
    defaults: { amount: '0.02 BNB', minAge: '10 min', risk: 'GREEN only' },
  },
  {
    id: 'momentum',
    name: 'Momentum',
    icon: '\u{26A1}',
    color: '#F0B90B',
    desc: 'Watches volume spikes and social momentum. Enters faster, trades AMBER if strong.',
    defaults: { amount: '0.05 BNB', minAge: '3 min', risk: 'GREEN + AMBER' },
  },
  {
    id: 'sniper',
    name: 'Sniper',
    icon: '\u{1F3AF}',
    color: '#F6465D',
    desc: 'Reacts to launch signals within minutes. Bonding curve only. Approve-each default.',
    defaults: { amount: '0.01 BNB', minAge: 'None', risk: 'Bonding curve' },
  },
]

export default function PersonaSelector({ selected, onSelect }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {PERSONAS.map((persona) => {
        const isActive = selected === persona.id
        return (
          <button
            key={persona.id}
            onClick={() => onSelect(persona.id)}
            className={`p-4 rounded-xl border-2 text-left cursor-pointer transition-all ${
              isActive
                ? 'border-[var(--accent-gold)] bg-[rgba(240,185,11,0.08)]'
                : 'border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--bg-hover)]'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{persona.icon}</span>
              <span
                className="font-semibold"
                style={{ color: isActive ? persona.color : 'var(--text-primary)' }}
              >
                {persona.name}
              </span>
            </div>
            <p className="text-[var(--text-secondary)] text-sm mb-3">{persona.desc}</p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(persona.defaults).map(([key, val]) => (
                <span
                  key={key}
                  className="text-xs px-2 py-0.5 rounded bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
                >
                  {val}
                </span>
              ))}
            </div>
          </button>
        )
      })}
    </div>
  )
}
