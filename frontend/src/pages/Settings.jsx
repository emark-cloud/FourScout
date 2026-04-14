import { useState, useEffect } from 'react'
import PersonaSelector from '../components/PersonaSelector'
import { getConfig, updateConfig, updateConfigBulk } from '../services/api'

const APPROVAL_MODES = [
  { id: 'approve_each', label: 'Approve Each', desc: 'Every trade requires explicit approval' },
  { id: 'approve_per_session', label: 'Per Session', desc: 'First trade approved, rest auto-execute' },
  { id: 'budget_threshold', label: 'Budget Threshold', desc: 'Auto under threshold, approve above' },
  { id: 'monitor_only', label: 'Monitor Only', desc: 'No trades, recommendations only' },
]

export default function Settings() {
  const [config, setConfig] = useState({})
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getConfig().then(setConfig).catch(console.error)
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateConfigBulk(config)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e) {
      console.error('Save error:', e)
    } finally {
      setSaving(false)
    }
  }

  const update = (key, value) => {
    setConfig((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-xl font-bold text-[var(--text-primary)] mb-6">Settings</h1>

      {/* Persona */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-3">Trading Persona</h2>
        <PersonaSelector
          selected={config.persona}
          onSelect={(id) => update('persona', id)}
        />
      </section>

      {/* Approval Mode */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-3">Approval Mode</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {APPROVAL_MODES.map((mode) => (
            <button
              key={mode.id}
              onClick={() => update('approval_mode', mode.id)}
              className={`p-3 rounded-lg border text-left cursor-pointer transition-all ${
                config.approval_mode === mode.id
                  ? 'border-[var(--accent-gold)] bg-[rgba(240,185,11,0.08)]'
                  : 'border-[var(--border)] bg-[var(--bg-card)] hover:border-[var(--bg-hover)]'
              }`}
            >
              <div className="font-medium text-sm text-[var(--text-primary)]">{mode.label}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-0.5">{mode.desc}</div>
            </button>
          ))}
        </div>
      </section>

      {/* Budget Caps */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-3">Budget Caps</h2>
        <div className="bg-[var(--bg-card)] rounded-xl p-4 space-y-4">
          {[
            { key: 'max_per_trade_bnb', label: 'Max per trade (BNB)', type: 'number', step: '0.01' },
            { key: 'max_per_day_bnb', label: 'Max per day (BNB)', type: 'number', step: '0.1' },
            { key: 'max_active_positions', label: 'Max active positions', type: 'number', step: '1' },
            { key: 'max_slippage_pct', label: 'Max slippage (%)', type: 'number', step: '0.5' },
            { key: 'cooldown_seconds', label: 'Cooldown (seconds)', type: 'number', step: '10' },
            { key: 'min_liquidity_usd', label: 'Min liquidity (USD)', type: 'number', step: '100' },
          ].map(({ key, label, type, step }) => (
            <div key={key} className="flex items-center justify-between">
              <label className="text-sm text-[var(--text-secondary)]">{label}</label>
              <input
                type={type}
                step={step}
                value={config[key] || ''}
                onChange={(e) => update(key, e.target.value)}
                className="w-32 bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1.5 text-sm text-[var(--text-primary)] text-right outline-none focus:border-[var(--accent-gold)]"
              />
            </div>
          ))}
        </div>
      </section>

      {/* Save button */}
      <button
        onClick={handleSave}
        disabled={saving}
        className="w-full bg-[var(--accent-gold)] text-black font-semibold py-3 rounded-xl cursor-pointer hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Settings'}
      </button>
    </div>
  )
}
