import { Link } from 'react-router-dom'

const STEPS = [
  {
    n: '1',
    title: 'Scan',
    body: 'FourScout polls Four.meme every 30 seconds, picking up fresh launches the moment they hit the bonding curve.',
  },
  {
    n: '2',
    title: 'Score',
    body: 'An 8-signal deterministic engine grades each token GREEN / AMBER / RED — creator history, holders, velocity, liquidity, tax, volume, social, market.',
  },
  {
    n: '3',
    title: 'Decide',
    body: 'Gemini 2.5 Flash turns signals into a plain-English rationale. You approve, reject, or let your persona auto-trade within hard budget caps.',
  },
  {
    n: '4',
    title: 'Track',
    body: 'Filled positions get PnL checks every 60 seconds plus AI exit analysis every 5 minutes — with optional auto-sell at your take-profit and stop-loss thresholds.',
  },
]

const FEATURES = [
  {
    title: '8-signal risk engine',
    body: 'Creator wallet history, holder concentration, bonding velocity, liquidity depth, tax flags, volume consistency, social sentiment, and market context — all deterministic, all weighted.',
  },
  {
    title: '3 personas × 4 approval modes',
    body: 'Conservative, Momentum, or Sniper — each with its own risk tolerance and age filters. Pick approve-each, per-session, budget-threshold, or monitor-only.',
  },
  {
    title: 'AI depth, not just labels',
    body: 'Gemini-powered chat advisor, AMBER deep-analysis escalation, and AI-driven exit checks. The LLM explains and advises — the rules engine decides.',
  },
  {
    title: 'ERC-8004 agent identity',
    body: 'On-chain registered agent wallet unlocks Four.meme AI Agent Mode exclusive phases, with hard server-side budget caps keeping every trade in bounds.',
  },
]

export default function Landing() {
  return (
    <div className="animate-fade-in-up">
      {/* Hero */}
      <section className="text-center pt-12 pb-20 px-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--bg-card)] border border-[var(--border)] mb-6">
          <span className="w-2 h-2 rounded-full bg-[var(--accent-green)] animate-pulse-glow" />
          <span className="text-xs text-[var(--text-secondary)]">Live on BNB Chain</span>
        </div>
        <h1 className="text-4xl sm:text-6xl font-bold text-[var(--text-primary)] tracking-tight mb-4">
          Four<span className="text-[var(--accent-gold)]">Scout</span>
        </h1>
        <p className="text-lg sm:text-xl text-[var(--text-primary)] font-medium mb-3">
          Your AI co-pilot for Four.meme memecoins
        </p>
        <p className="max-w-2xl mx-auto text-sm sm:text-base text-[var(--text-secondary)] leading-relaxed mb-8">
          FourScout scans every new Four.meme launch, scores risk across 8 on-chain signals, and explains
          what it finds in plain English — so you decide fast without getting rugged.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            to="/dashboard"
            className="bg-[var(--accent-gold)] text-black font-semibold rounded-lg px-6 py-3 text-sm no-underline hover:opacity-90 transition-opacity"
          >
            Launch Dashboard &rarr;
          </Link>
          <a
            href="https://github.com/emark-cloud/FourScout"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm px-4 py-3 no-underline transition-colors"
          >
            View on GitHub
          </a>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 px-4 border-t border-[var(--border)]">
        <h2 className="text-center text-xs uppercase tracking-widest text-[var(--text-secondary)] mb-2">
          How it works
        </h2>
        <p className="text-center text-2xl font-semibold text-[var(--text-primary)] mb-10">
          Four steps from launch to exit
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 max-w-6xl mx-auto">
          {STEPS.map((s) => (
            <div key={s.n} className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)]">
              <div className="w-10 h-10 rounded-lg bg-[var(--bg-primary)] flex items-center justify-center text-[var(--accent-gold)] font-bold text-lg mb-4">
                {s.n}
              </div>
              <h3 className="text-[var(--text-primary)] font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Why FourScout */}
      <section className="py-16 px-4 border-t border-[var(--border)]">
        <h2 className="text-center text-xs uppercase tracking-widest text-[var(--text-secondary)] mb-2">
          Why FourScout
        </h2>
        <p className="text-center text-2xl font-semibold text-[var(--text-primary)] mb-10">
          Built for the Four.meme edge
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl mx-auto">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-[var(--bg-card)] rounded-xl p-6 border border-[var(--border)] card-hover"
            >
              <h3 className="text-[var(--text-primary)] font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Closing CTA */}
      <section className="py-16 px-4 border-t border-[var(--border)] text-center">
        <h2 className="text-2xl font-semibold text-[var(--text-primary)] mb-3">
          Ready to scout?
        </h2>
        <p className="text-sm text-[var(--text-secondary)] mb-6 max-w-md mx-auto">
          Jump into the live feed — scoring, rationales, and approvals wired up end-to-end.
        </p>
        <Link
          to="/dashboard"
          className="inline-block bg-[var(--accent-gold)] text-black font-semibold rounded-lg px-6 py-3 text-sm no-underline hover:opacity-90 transition-opacity"
        >
          Launch Dashboard &rarr;
        </Link>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-[var(--border)] text-center">
        <div className="flex items-center justify-center gap-6 text-xs text-[var(--text-secondary)]">
          <a
            href="https://github.com/emark-cloud/FourScout"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[var(--text-primary)] no-underline transition-colors"
          >
            GitHub
          </a>
          <a
            href="https://dorahacks.io/hackathon/four-meme-ai-sprint"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[var(--text-primary)] no-underline transition-colors"
          >
            Four.Meme AI Sprint
          </a>
          <span>Built on BNB Chain</span>
        </div>
      </footer>
    </div>
  )
}
