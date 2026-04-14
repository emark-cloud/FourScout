# MemeGuard — Build TODO

## Phase 1: Foundation
- [ ] Project scaffolding: backend (FastAPI + requirements.txt) + frontend (React/Vite + Tailwind)
- [ ] Backend config.py (Pydantic Settings, .env loading, contract address constants)
- [ ] Database schema (SQLite: tokens, scans, positions, trades, avoided, config, watchlist, activity, token_snapshots)
- [ ] .env.example + .gitignore
- [ ] Four.meme CLI wrapper (`backend/clients/fourmeme_cli.py` — subprocess around @four-meme/four-meme-ai)
- [ ] Install Four.meme CLI locally (`fourmeme-cli/` npm package)
- [ ] Contract ABIs (TokenManager2, TokenManagerHelper3, AgentIdentifier, TaxToken, ERC20 — lite versions)
- [ ] BSC Web3 client (`backend/clients/bsc_web3.py` — get_token_info, get_holder_balances, get_creator_history, is_tax_token, is_agent)
- [ ] Four.meme REST API client (`backend/clients/fourmeme_api.py` — search_tokens, get_token, get_rankings)
- [ ] Market context client (`backend/clients/market_api.py` — BNB price, Fear & Greed)
- [ ] Scanner service (`backend/services/scanner.py` — APScheduler 30s polling + event monitoring)
- [ ] Risk scoring engine v1 — 3 signals: creator history, holder concentration, liquidity depth
- [ ] Backend routes: GET /api/tokens, GET /api/tokens/:addr, GET/PUT /api/config, GET /api/activity
- [ ] Frontend: Tailwind dark theme config (Binance-inspired colors)
- [ ] Frontend: App.jsx with React Router (6 routes) + WagmiProvider (BSC chain)
- [ ] Frontend: Navbar, TokenCard, RiskBadge, PersonaSelector, BudgetBar components
- [ ] Frontend: useWallet hook (wagmi BSC), useWebSocket hook
- [ ] Frontend: Dashboard page (live token feed + persona badge + budget bar + stats)
- [ ] Frontend: Settings page (persona selector + budget caps + approval mode)
- [ ] Frontend: api.js service (backend REST client)
- [ ] **Verify:** Connect wallet, select persona, see live scored token feed

## Phase 2: Brain
- [ ] Complete risk engine — add 5 signals: bonding curve velocity, tax token flags, volume consistency, social signal, market context
- [ ] LLM service (`backend/services/llm_service.py` — Gemini 2.0 Flash, provider abstraction)
- [ ] Persona action engine (`backend/services/persona_engine.py` — 3 persona configs, decide_action)
- [ ] Transaction builder (`backend/services/tx_builder.py` — prepare_buy/sell with quote + slippage)
- [ ] Approval gate system (`backend/services/approval_gate.py` — 4 modes)
- [ ] Trade executor (`backend/services/executor.py` — execute via CLI, enforce caps, record, notify)
- [ ] Position tracker (`backend/services/position_tracker.py` — APScheduler 60s, update prices, compute PnL)
- [ ] Backend routes: POST /api/actions/approve, POST /api/actions/reject, GET /api/positions
- [ ] Frontend: OpportunityDetail page (risk breakdown + LLM rationale + creator history + approve/reject)
- [ ] Frontend: ApprovalModal component (TX preview: amount, slippage, gas)
- [ ] Frontend: Positions page (active positions with PnL + agent recommendations)
- [ ] Frontend: Activity page (chronological event feed)
- [ ] WebSocket integration (scanner → risk → persona → executor all broadcast events)
- [ ] **Verify:** End-to-end trade: find token → score → explain → approve → execute → track position

## Phase 3: Polish + Demo
- [ ] "What I Avoided" tracker (`backend/services/avoided_tracker.py` — 1h/6h/24h price checks, confirmed rug detection)
- [ ] Avoided routes + Avoided page + AvoidedCard component (savings tally + per-token cards)
- [ ] Behavioral nudge (overrides table, 24h outcome check, summary widget on Dashboard)
- [ ] ERC-8004 agent registration (agent_identity.py + Settings UI button)
- [ ] Watchlist CRUD (routes + Settings UI + scanner integration)
- [ ] Visual polish (animations, hover effects, bonding curve bars, responsive layout)
- [ ] Backend Dockerfile (Python + Node.js) → Railway deployment
- [ ] Frontend → Vercel deployment
- [ ] Demo seed script (pre-populate avoided rugs for demo)
- [ ] README.md (architecture, screenshots, setup instructions)
- [ ] Demo video recording (3-5 min, follow script in Memeguard.md Section 12)
- [ ] DoraHacks BUIDL submission (GitHub repo + demo video link)
- [ ] **Verify:** Full demo flow: wallet → 8004 register → persona → live feed → approve trade → avoided rugs → behavioral summary
