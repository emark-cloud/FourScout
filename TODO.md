# FourScout — Build TODO

## Phase 1: Foundation (COMPLETE)
- [x] Project scaffolding: backend (FastAPI + requirements.txt) + frontend (React/Vite + Tailwind)
- [x] Backend config.py (Pydantic Settings, .env loading, contract address constants)
- [x] Database schema (SQLite: tokens, scans, positions, trades, avoided, config, watchlist, activity, token_snapshots)
- [x] .env.example + .gitignore
- [x] Four.meme CLI wrapper (`backend/clients/fourmeme_cli.py` — subprocess around @four-meme/four-meme-ai)
- [x] Install Four.meme CLI locally (`fourmeme-cli/` npm package)
- [x] Contract ABIs (TokenManager2, TokenManagerHelper3, AgentIdentifier, TaxToken, ERC20 — lite versions)
- [x] BSC Web3 client (`backend/clients/bsc_web3.py` — get_token_info, get_holder_balances, get_creator_history, is_tax_token, is_agent)
- [x] Four.meme REST API client (`backend/clients/fourmeme_api.py` — search_tokens, get_token, get_rankings)
- [x] Market context client (`backend/clients/market_api.py` — BNB price, Fear & Greed)
- [x] Scanner service (`backend/services/scanner.py` — 30s polling + event monitoring)
- [x] Risk scoring engine — all 8 signals with weighted aggregation
- [x] LLM service (Gemini 2.5 Flash, provider abstraction, fallback rationale)
- [x] Persona engine (3 personas, decide_action rules)
- [x] Trade executor (buy/sell via CLI, position/trade recording)
- [x] Backend routes: tokens, config, activity, positions, actions, avoided, watchlist
- [x] Frontend: Tailwind dark theme config (Binance-inspired colors)
- [x] Frontend: App.jsx with React Router (6 routes) + WagmiProvider (BSC chain)
- [x] Frontend: Navbar, TokenCard, RiskBadge, PersonaSelector, BudgetBar components
- [x] Frontend: useWallet hook (wagmi BSC), useWebSocket hook
- [x] Frontend: Dashboard page (live token feed + persona badge + budget bar + stats)
- [x] Frontend: Settings page (persona selector + budget caps + approval mode)
- [x] Frontend: OpportunityDetail page (8-signal breakdown + rationale + approve/reject)
- [x] Frontend: Positions, Avoided (stats + cards), Activity feed pages
- [x] Frontend: api.js service (backend REST client)
- [x] WebSocket: auto-reconnecting, live push for new tokens and risk scores
- [x] **Verified:** Scanner discovering and scoring real Four.meme tokens with GREEN/AMBER/RED grades

## Phase 2: The Brain (COMPLETE)
**Goal:** End-to-end trade loop with AI depth and position tracking.

### Core Pipeline (carry-over)
- [x] Complete risk scoring engine: all 8 signals
- [x] LLM integration (Gemini 2.5 Flash) for rationale generation
- [x] Opportunity detail page (full risk breakdown + rationale + action)
- [x] Persona action engine (rules that map score + persona → action)
- [x] Approval gate system (4 modes — `approval_gate.py`)
- [x] Trade executor (buy/sell via CLI, with slippage protection via quote)
- [x] Activity feed page
- [x] WebSocket for live updates
- [x] Transaction builder integration: quote via CLI → slippage calc → TxPreview display (`tx_builder.py`)
- [x] Approval modal: TX preview with amount, slippage, estimated tokens, min tokens, approve/reject
- [x] Position tracker background job: update prices, compute PnL, propose exits (`position_tracker.py`)
- [x] Auto-propose actions: scanner → score → persona decides → approval gate → pending_action + broadcast
- [x] End-to-end buy loop: scanner → score → propose → approve → buy on-chain → position tracked (verified with 0.0001 BNB)

### Sell Flow & Position Management
- [x] Complete sell executor: sell quote for slippage protection, position closure, trade recording, PnL fields
- [x] Configurable take-profit/stop-loss thresholds (user-settable in Settings, replaces hardcoded 100%/-50%)
- [x] Auto-sell mode: automatic execution at thresholds without requiring approval
- [x] AI-driven position monitoring: Gemini analyzes positions every 5 min, proposes exits with reasoning
  - Drift detection: PnL approaching thresholds, stale positions, holder concentration changes
  - Capped at 3 LLM calls per cycle
- [x] Sell action approve/reject UI on Positions page
- [x] End-to-end sell loop: position tracker proposes → approve → execute on-chain → position closed (verified with 0.0001 BNB)

### AI Depth (competitive edge — targets Innovation criterion)
- [x] Interactive AI chat advisor: backend `/api/chat` endpoint + frontend ChatPanel component
  - Context-aware: pulls token risk data, positions, persona config into prompt
  - Conversational memory within session (last N messages)
  - Token-scoped chat on OpportunityDetail page
  - Suggested questions for new users
- [x] Multi-signal narrative synthesis: enhanced LLM prompt that correlates signals
  - Cross-signal pattern detection ("serial creator + high concentration = pump-and-dump setup")
  - Cohesive narrative rationale instead of per-signal summaries
- [x] Escalation pipeline: quick deterministic scan for GREEN/RED, deep AI analysis only for AMBER tokens
  - `deep_analyze_amber()` returns recommendation (lean_buy/lean_skip/watch) with confidence + analysis

### Real-Time Alerting
- [x] Toast notification system: real-time alerts for WebSocket events (trade_executed, action_proposed, risk_alert)
  - Position update toasts filtered to milestones only (50%+, 100%+, -40%+) to prevent spam
  - Max 5 visible, auto-dismiss after 5s, Binance-themed colors
- [x] `action_proposed` — new trade opportunity pending approval
- [x] `trade_executed` — buy/sell completed with tx details
- [x] `position_update` — PnL change (periodic, from position tracker)
- [x] `risk_alert` — token grade changed on rescore
- [x] `avoided_update` — "dodged a bullet" notification (implemented in Phase 3 avoided tracker)

### Verify Phase 2
- [x] **Auto-propose pipeline:** scanner → score → persona → approval gate → pending_action (verified: 10+ pending actions auto-created)
- [x] **Full buy loop:** approve → execute → track position (verified: 0.0001 BNB trade, tx on-chain, position recorded)
- [x] **Full sell loop:** position tracker proposes exit → approve → execute on-chain → position closed (verified with 0.0001 BNB, tx 0x3a7f...6e9f)
- [x] **AI advisor:** chat endpoint + frontend ChatPanel (graceful fallback without Gemini key)
- [x] **Live dashboard:** WebSocket events update UI without refresh
- [x] **Gemini 2.5 Flash migration:** upgraded from deprecated 2.0 Flash, thinking_budget=0 fix, all 6 AI integration points verified

## Phase 3: Polish & Demo Features
**Goal:** Demo-ready with killer differentiators and visual polish. Ordered by judging impact.

### High Priority (Differentiators)
- [x] ERC-8004 agent identity registration (`agent_identity.py` + Settings UI section + on-chain verification)
- [x] "What I Avoided" background job: check red-flagged token prices at 1h/6h/24h, confirmed rug detection, `avoided_update` toast
- [x] Risk visualization: radar chart for 8-signal breakdown (recharts RadarChart on OpportunityDetail)
- [ ] Deployment: Backend `Dockerfile` + `docker-compose.yml` (Python + Node.js for Four.meme CLI, SQLite volume mount) → Railway / Render / self-host; Frontend → Vercel (`VITE_API_BASE` → backend URL). See README "Deployment" section.

### Medium Priority (Completeness)
- [x] Behavioral nudge: track overrides (approve risky / reject safe), show outcome summary on Dashboard
- [x] Watchlist management UI on Settings page (add/remove creator + token addresses)
- [x] Volume consistency signal: real implementation using on-chain Transfer event analysis (wash trading detection)

### Demo & Submission
- [ ] Demo seed script (pre-populate avoided rugs for compelling demo)
- [x] Visual polish: card fade-in animations, hover glow, pulsing scanner dot, responsive grid
- [x] README.md (architecture diagram, feature list, setup instructions)
- [ ] Demo video recording (3-5 min, follow script in FourScout.md Section 12)
- [ ] DoraHacks BUIDL submission (GitHub repo + demo video link)

### Verify Phase 3
- [x] **Playwright UI pass:** dashboard feed, token detail radar + 8 signals + AMBER deep-analysis narrative, avoided stats, settings (8004 card, persona, approval, exit strategy, budget, watchlist), AI chat panel (graceful Gemini-503 fallback) — all render correctly
- [x] **Fixed during verification:** event-loop blocking on sync Web3 calls (commit `3476eb4`); SQLite `database is locked` under concurrent scoring + ghost-token AMBER mis-grading (commit `295bd0f`) — avoided tracker now auto-populates (39+ tokens flagged live)
- [x] **Wallet-gated demo flow:** 8004 register tx (agent wallet `0xECf5…Bb25` registered on BSC mainnet) + trade approve-sign (position_id 4, 13,069 ORDI, entry 0.0001 BNB, tx `0x8a9e876852b6368fbc1a0bb027eddf1b2043f9882af469653112314c2771dbdb`)
- [x] **LLM cost-reduction verification (2026-04-17):** confirmed live against refreshed Gemini key — (1) `POST /api/chat` returned `{"reply":"LIVE OK"}` on first call; (2) `generate_rationale` returned a 435-char narrative ending cleanly at a period (no truncation at 200 tokens); `deep_analyze_amber` returned parseable JSON with a complete `analysis` paragraph (no truncation at 256 tokens); (3) `_should_call_ai` truth table verified end-to-end: empty→True, just-called-same-pnl→False, +1%→False (below 3% delta), +4%→True (above 3% delta), 16-min-old→True (past cooldown); (4) `settings.ai_exit_interval_cycles=10` and `do_ai = cycle % 10 == 0` gate — first exit-AI batch fires at cycle 10 (minute 10). Commit `f4523b4`.
- [ ] **Community voting appeal:** deployed, polished, screenshot-worthy

## Phase 3.5: Agent Memory & Continuity
**Goal:** Close the memory loops so FourScout remembers past interactions, maintains state across restarts, and has its judgment improve as trades close. Aligned with Four.meme team AMA guidance on state, continuity, and the `input → reason → act → memory update` loop. Full design in `.claude/plans/tidy-mixing-marble.md`.

### Persistent interaction memory
- [ ] **Persistent chat memory** — new `chat_messages` table `(id, token_address NULLABLE, role, content, created_at)` with index on `(token_address, id)`. Replace `_chat_history` module global in `chat_service.py` with DB reads/writes. Scope by `token_address` so OpportunityDetail chats are per-token and the Dashboard chat is global. Verification: send 3 chats, restart backend, confirm history survives and per-token scoping holds.
- [ ] **Rejection reason capture** — add `rejection_reason TEXT` to `pending_actions`. `POST /api/actions/reject` accepts optional `{ reason }`. Frontend reject modal gets an optional textarea (500 char max). Surface top 3 rejection reasons (last 7d) on the Behavioral Nudge card.

### Closed feedback loops
- [ ] **Override-aware nudge in rationale** — new helper `backend/services/override_stats.py` with SQL aggregates over `overrides` + `positions`. `persona_engine.decide_action` appends a one-line nudge to the proposal's rationale: *"You've approved 4 RED tokens in the last 7 days; 3 closed at >50% loss."* Pure observability — does not change the decision (keeps the deterministic core per AMA guidance on controllable logic).
- [ ] **Persist AI exit-check cooldown across restarts** — add `last_ai_check_at TEXT` and `last_ai_pnl_pct REAL` columns to `positions`. `position_tracker._should_call_ai` reads/writes these columns on the position row; drop the in-memory `_last_ai_check` dict. Fixes the restart-storm where every position triggers a fresh LLM call on the first cycle after a restart.

### Learning loops (demo-visible "improves over time")
- [ ] **Creator reputation cache with outcome feedback** — new `creator_reputation` table `(creator_address PK, launch_count, avg_24h_outcome_pct, confirmed_rugs, profitable_closes, losing_closes, last_updated)`. `risk_engine.score_creator_history` checks cache first (1-hour TTL); only recomputes from chain on miss. `executor.py` updates `profitable_closes`/`losing_closes` on position close. `avoided_tracker.py` updates `confirmed_rugs` on 24h rug confirmation. Signal scoring folds these counters into the creator score so a creator with many rugs scores worse than one with one rug. Kills the ~50k-block BSC query on every scan for known creators.
- [ ] **Signal accuracy tracker** — new `signal_outcomes` table capturing entry signal pattern + outcome (`trade_closed` with PnL% or `avoided_24h` with price change & rug flag). Writes from `executor.close_position` and `avoided_tracker` 24h resolution. `risk_engine.score_token` runs one aggregate on each scan and feeds *"Historical: 3 of your 4 AMBER tokens with creator-score ≤3 closed at >50% loss"* into the LLM rationale prompt (and into the deterministic fallback so demo still works without Gemini credits). Include a backfill migration on startup that populates retroactively from existing closed positions + 24h-resolved avoided tokens, so demo-day doesn't need 30 days of operation to be interesting.

### Verify Phase 3.5
- [ ] Chat persistence survives restart; per-token scoping holds
- [ ] Rejection reason is persisted and surfaces on Behavioral Nudge card
- [ ] Override-aware nudge appears in proposal rationale after 3+ overrides recorded
- [ ] Restarting backend mid-position does NOT trigger a fresh AI exit check within the cooldown window
- [ ] Second scan of same creator within 1h logs a cache hit (no BSC query)
- [ ] Closing a losing position increments `creator_reputation.losing_closes` and worsens that creator's score on the next scan
- [ ] LLM rationale prompts log shows the historical-outcome line being interpolated
- [ ] Backfill populates `signal_outcomes` on a fresh clone from existing closed positions + 24h-resolved avoided rows
- [ ] No regressions: risk engine scoring latency unchanged or faster; existing deterministic TP/SL unchanged; no increase in LLM call counts

### Out of scope (deliberate)
- Semantic/vector chat memory (linear last-N per token is sufficient for trading-decision chat)
- RL-style policy updates (AMA advised against complex strategy optimization)
- Populating the dormant `token_snapshots` table (velocity signal already works; orthogonal to the memory theme)
- Cross-session user profile learning (post-hackathon direction)
- Agent-to-agent coordination (ERC-8004 registration makes FourScout discoverable; active coordination is a Phase 4+ direction)

## Phase 4: Non-Custodial Session Keys (Roadmap — post-hackathon)
**Goal:** Evolve from single-tenant self-hosted (one `PRIVATE_KEY` per deployment) to hosted multi-tenant with cryptographically bounded delegation. Design documented in `FourScout.md` §18.

### Stack
- [ ] ZeroDev Kernel v3 smart account on BSC mainnet (chain 56), EntryPoint v0.7
- [ ] `@zerodev/permissions` session-key module with composable policies: `toCallPolicy` (whitelist Four.meme contracts + selectors), `toSpendingLimitPolicy` (max BNB over session), `toRateLimitPolicy` (userOps/hour cap), `toTimestampPolicy` (7-day expiry)
- [ ] Pimlico bundler integration (BSC mainnet)

### Backend
- [ ] `session-signer/` Node.js sidecar (TypeScript) — `POST /userop` endpoint that builds, signs with session key, submits via Pimlico, returns tx hash
- [ ] Python backend refactor: replace `fourmeme buy/sell/8004-register` signing calls with `httpx` calls to session-signer. `fourmeme_cli.py` keeps all read-only commands (quote-buy, quote-sell, tax-info, events, rankings, token-info).
- [ ] Session key storage: encrypted-at-rest in DB (libsodium sealed box for self-host; KMS envelope for hosted)
- [ ] Config schema: add `smart_account_address`, `session_key_policy_hash`, `session_expires_at`; deprecate direct `PRIVATE_KEY` usage for signing

### Frontend (multi-step onboarding wizard)
- [ ] Connect EOA → compute counterfactual Kernel address → show fund-this-address instruction
- [ ] Generate ephemeral session-key keypair in-browser
- [ ] Prompt MetaMask to sign session-key grant with policy constraints pulled from current Budget Caps config
- [ ] POST session key + policy metadata to backend
- [ ] Settings page: session status card (expiry, remaining cap, active validator) + Revoke button (signs `disableValidator` via MetaMask)

### Migration & Ops
- [ ] Dual-mode backend: detect `PRIVATE_KEY` fallback for self-host vs. session-key mode for hosted; swap executor at runtime
- [ ] userOp failure telemetry: distinguish bundler reverts, policy rejections, session expiry from generic tx errors
- [ ] Docs: migration guide for self-hosted users (optional path; `PRIVATE_KEY` mode remains supported)

### Open Questions (resolve during implementation)
- [ ] Policy upgrade UX: does raising `max_per_day_bnb` require a new grant signature, or can the backend layer sub-policies?
- [ ] Session-signer deployment: separate Docker service vs. supervised process inside backend container?
- [ ] Paymaster use: does gasless onboarding (first userOp sponsored) add enough value to justify the integration?
