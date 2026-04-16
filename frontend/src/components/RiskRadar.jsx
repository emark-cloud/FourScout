import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'

const SIGNAL_LABELS = {
  creator_history: 'Creator',
  holder_concentration: 'Holders',
  liquidity: 'Liquidity',
  bonding_velocity: 'Velocity',
  tax_token: 'Tax',
  volume_consistency: 'Volume',
  social_signal: 'Social',
  market_context: 'Market',
}

export default function RiskRadar({ riskDetail }) {
  if (!riskDetail || Object.keys(riskDetail).length === 0) return null

  const data = Object.entries(riskDetail).map(([key, signal]) => ({
    signal: SIGNAL_LABELS[key] || key.replace(/_/g, ' '),
    score: signal.score || 0,
    fullMark: 10,
  }))

  // Calculate fill color based on average score
  const avg = data.reduce((sum, d) => sum + d.score, 0) / data.length
  const fillColor = avg >= 6.5 ? '#0ECB81' : avg >= 4 ? '#F0B90B' : '#F6465D'

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="var(--border)" />
          <PolarAngleAxis
            dataKey="signal"
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tickCount={3}
            tick={{ fill: 'var(--text-secondary)', fontSize: 9 }}
          />
          <Radar
            name="Risk Score"
            dataKey="score"
            stroke={fillColor}
            fill={fillColor}
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
