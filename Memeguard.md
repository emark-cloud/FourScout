# MemeGuard — Four.meme AI Agent Console

## Synthesized MVP Specification

**Hackathon:** Four.Meme AI Sprint (DoraHacks, $50K pool, deadline April 30 2026)
**Builder:** Solo + Claude Code
**Chain:** BNB Chain (BSC)
**Submission requires:** GitHub repo + demo video

---

## 1. What This Is

MemeGuard is a persona-based AI trading agent for Four.meme that scans new token launches, scores them for risk and opportunity in plain language, and executes trades only within user-approved limits.

**Core loop:**

```
detect opportunity → score risk → explain in plain language → persona filters → prepare transaction → user approves → execute
```

**Three things it does well:**

1. **Monitor** new Four.meme launches and BNB/PancakeSwap market context in real time
2. **Score and explain** risk, momentum, and rug signals using on-chain + sentiment signals
3. **Execute trades** through approval gates, under hard budget caps, filtered by a chosen persona

---

## 2. Target User

**Primary:** Existing memecoin trader on Four.meme who is tired of manually vetting hundreds of launches and wants an AI co-pilot that flags opportunity and danger.

**Secondary:** Token creator who wants to monitor their own token's health after launch.

---

## 3. Personas

Three presets. No freeform customization in v1.

### Conservative

- Low trade frequency
- Smaller position sizes (default 0.02 BNB)
- Requires green risk score + strong volume confirmation
- Avoids tokens under 10 minutes old
- Skips anything with holder concentration >40%
- **Best for:** users who want fewer trades and more safety

### Momentum

- Watches volume spikes, social momentum, and liquidity changes
- Enters faster than Conservative (default 0.05 BNB)
- Will trade amber-scored tokens if momentum is strong
- Still respects all budget caps and approval gates
- **Best for:** traders who want speed without full automation

### Sniper

- Reacts to new listings and strong launch signals within minutes
- Highest risk tolerance
- Smallest default size (0.01 BNB) as counterbalance
- Strictest approval mode (approve-each by default)
- Only enters during bonding curve phase
- **Best for:** advanced users who want launch-speed execution

---

## 4. Features

### A. Opportunity Scanner

The agent monitors in real time:

- New Four.meme token launches (via Four.meme public API)
- Token migration / graduation events (bonding curve → PancakeSwap listing)
- Liquidity additions and removals
- Price and volume spikes
- PancakeSwap trading activity on graduated tokens
- Basic social sentiment from linked Twitter/Telegram (lightweight — not a full suite)

**Output per opportunity:**

- What happened (one-line summary)
- Why it matters (plain-language rationale, LLM-generated)
- Risk score (green / amber / red)
- What the selected persona would do (buy / skip / monitor)

### B. Risk Scoring Engine

Concrete signals, not abstract AI. Each scored independently, combined into an overall green/amber/red grade.

| Signal | What It Checks | Weight |
|--------|----------------|--------|
| **Creator history** | Has this wallet launched tokens before? Did those tokens dump >80% within 24h? How many prior launches? | High |
| **Bonding curve velocity** | Is the curve filling unusually fast (suggesting coordinated/bot buying)? Compare fill rate to historical average. | High |
| **Holder concentration** | Top 5 wallets holding >X% of supply. Single wallet >20% = red flag. | High |
| **Liquidity depth & age** | Is there enough liquidity to exit? Has liquidity been present for <5 minutes? | Medium |
| **Tax token flags** | Does the token use Four.meme's TaxToken contract? What are the fee parameters? Unusual sell tax = danger. | Medium |
| **Volume consistency** | Is volume real or wash-traded? Look for suspiciously regular buy patterns. | Medium |
| **Social signal** | Does the token have linked social accounts? Are they active? Sentiment positive or pump-language? | Low |
| **Market context** | Fear & Greed Index, BNB 24h trend. Bear market = higher bar for entry. | Low |

**Output:**

- Overall grade: Green (low risk) / Amber (moderate) / Red (high risk / likely rug)
- One-line explanation: "Creator has launched 4 tokens in 48h, all dumped >90%"
- Primary risk factor highlighted

### C. Persona-Based Action Engine

Based on the selected persona, the agent proposes exactly one of:

- **Buy** — with exact amount and slippage
- **Skip** — with reason
- **Monitor** — add to watchlist, check again in N minutes
- **Take profit** — partial or full exit
- **Exit** — sell entire position
- **Reduce exposure** — sell partial position

No complex portfolio theory. One action, one reason, one approval button.

### D. Approval Gates

Four modes, user-selectable:

| Mode | Behavior |
|------|----------|
| **Approve each** | Every trade requires explicit approval (default for Sniper) |
| **Approve per session** | First trade of each session requires approval, rest auto-execute within rules |
| **Budget threshold** | Auto-execute small trades, require approval when cumulative spend crosses a threshold |
| **Monitor only** | Agent scores and recommends, never prepares transactions. User trades manually. |

### E. Budget-Limited Autonomy

Hard caps that cannot be exceeded regardless of approval mode:

| Rule | Default | Configurable |
|------|---------|-------------|
| Max per trade | 0.05 BNB | Yes |
| Max per day | 0.3 BNB | Yes |
| Max active positions | 3 | Yes |
| Max trades per token | 1 entry | Yes |
| Min liquidity threshold | $500 | Yes |
| Max slippage | 5% | Yes |
| Cooldown between trades | 60 seconds | Yes |

### F. Wallet & Execution

- Connect existing wallet (MetaMask, WalletConnect)
- Or generate a hot wallet within the app (encrypted local storage)
- Prepare swap transactions with full preview (token, amount, slippage, estimated gas)
- Request wallet signature
- Execute after approval
- Optionally register wallet as ERC-8004 agent via Four.meme's `AgentIdentifier` contract (enables insider phase access)

### G. "What I Avoided" Log

This is the demo killer feature.

- Every token the agent scores red gets logged with a timestamp
- A background job checks each red-scored token 1h, 6h, and 24h later
- If the token dropped >70% or liquidity was pulled: confirmed rug
- Dashboard shows: "Avoided 8 rugs this week — estimated savings: 0.4 BNB"
- Visual feed of avoided tokens with before/after price

### H. Behavioral Nudge

When a user overrides the agent's recommendation:

- Log the override (user approved a red-scored token, or skipped a green one)
- Track the outcome
- Show a periodic summary: "You overrode 3 Danger signals this week. 2 of those tokens dropped 80%+"
- Lightweight — not a coaching system, just a feedback mirror

### I. Watchlist

Users can manually add:

- Specific tokens to monitor
- Specific creator wallets to track
- Launch patterns to flag (e.g., "alert me on any token with 'AI' in the name")

---

## 5. Non-Goals (v1)

Do NOT build:

- Full portfolio management / rebalancing
- Full social media intelligence suite
- Full creator analytics dashboard
- Arbitrary DeFi strategy backtesting
- Cross-chain support (BSC only)
- Freeform persona customization
- Autonomous trading without caps
- Token creation features (separate agent — don't dilute)
- Mobile app
- User accounts / auth system (wallet = identity)

---

## 6. User Flows

### Flow 1: First-Time Setup

```
Connect wallet
    → Pick persona (Conservative / Momentum / Sniper)
    → Set budget cap (or accept defaults)
    → Choose approval mode
    → Optional: register as ERC-8004 agent wallet
    → Land on scanner dashboard
```

### Flow 2: Finding a Trade

```
Agent detects new token or market signal
    → Scores risk (green / amber / red)
    → Generates plain-language rationale
    → Applies persona filter (buy / skip / monitor)
    → If buy: prepares transaction payload
    → Shows opportunity card with approve/reject buttons
    → User approves → agent executes
    → User rejects → agent logs and moves on
```

### Flow 3: Post-Trade Monitoring

```
Agent watches active position
    → Monitors price, volume, liquidity changes
    → Detects momentum loss or abnormal activity
    → Suggests hold / take profit / exit
    → User approves the next action
```

### Flow 4: Reviewing Avoided Risks

```
User opens "What I Avoided" tab
    → Sees tokens agent flagged red
    → Each shows current price vs. price at flag time
    → Confirmed rugs highlighted
    → Running tally of estimated savings
```

---

## 7. Web App Pages

### Dashboard (Home)

- Active persona badge + budget remaining
- Live opportunity feed (new launches, scored and ranked)
- Current positions with unrealized PnL
- Agent status indicator (scanning / idle / proposing)
- Quick stats: trades today, avoided rugs, budget used

### Opportunity Detail

- Token name, symbol, contract address, launch time
- Bonding curve progress (visual bar)
- Risk score breakdown (each signal scored)
- LLM-generated rationale (2-3 sentences)
- Creator wallet history (prior launches, outcomes)
- Recommended action from persona
- Approve / Reject buttons
- Transaction preview (amount, slippage, gas estimate)

### Positions

- Active positions with entry price, current price, PnL
- Agent's recommendation for each (hold / trim / exit)
- Approve action buttons per position

### What I Avoided

- Feed of red-scored tokens with timestamps
- Current status: price now vs. price at flag time
- Confirmed rug indicators
- Cumulative savings estimate

### Activity Feed

- Chronological log of:
  - Scans performed
  - Opportunities scored
  - Trades proposed
  - Trades approved / rejected
  - Trades executed
  - Alerts raised
  - User overrides (with outcome tracking)

### Settings

- Persona selection (switch anytime)
- Budget caps (all configurable)
- Approval mode
- Wallet management
- Agent wallet ERC-8004 registration
- Watchlist management
- Slippage / cooldown preferences

---

## 8. Architecture

### System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        React Frontend                            │
│  Dashboard │ Opportunity Detail │ Positions │ Avoided │ Settings │
│                                                                  │
│  Wallet Connection (wagmi/ethers)                                │
│  Approval Modal → Signature Request → TX Execution               │
└──────────────────────────┬───────────────────────────────────────┘
                           │ REST API + WebSocket (live feed)
┌──────────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                              │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │ Signal       │  │ Risk Scoring │  │ Persona Action     │      │
│  │ Ingestion    │──│ Engine       │──│ Engine             │      │
│  │ Service      │  │ (6 signals)  │  │ (Consv/Mom/Snipe)  │      │
│  └──────┬──────┘  └──────┬───────┘  └────────┬───────────┘      │
│         │                │                    │                   │
│  ┌──────▼──────┐  ┌──────▼───────┐  ┌────────▼───────────┐      │
│  │ Four.meme   │  │ LLM Service  │  │ Transaction        │      │
│  │ API Client  │  │ (Claude API) │  │ Builder            │      │
│  └─────────────┘  └──────────────┘  └────────────────────┘      │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │ BSC Web3    │  │ Avoided Log  │  │ Override Tracker    │      │
│  │ Provider    │  │ Service      │  │ (Behavioral Nudge)  │      │
│  └─────────────┘  └──────────────┘  └────────────────────┘      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐      │
│  │              SQLite (local-first storage)               │      │
│  │  tokens │ scans │ positions │ trades │ avoided │ config │      │
│  └────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────┘
                           │
                    BSC (BNB Chain)
              ┌────────────┼────────────┐
              │            │            │
        Four.meme    PancakeSwap   AgentIdentifier
        Contracts    Router        (ERC-8004)
```

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + Vite + Tailwind | Fast build, polished output, dark theme |
| Backend | Python FastAPI | Best Web3.py + pandas + LLM SDK access |
| Database | SQLite | Local-first, zero config, sufficient for MVP |
| On-chain | Web3.py | Four.meme ABIs (TokenManager2, AgentIdentifier, TaxToken) |
| AI/LLM | Anthropic Claude API | Rationale generation, token description analysis, sentiment |
| Wallet | wagmi + ethers.js (frontend) | Standard BSC wallet connection |
| Market Data | Four.meme API + Binance API + CoinGecko | Token feeds, prices, Fear & Greed |
| Deploy | Vercel (frontend) + Railway (backend) | Free tier sufficient for demo |

### Four.meme Integration Points

| Integration | Method | Purpose |
|-------------|--------|---------|
| New token feed | Four.meme public API | Discover launches in real time |
| Token metadata | Four.meme API (`/meme-api/v1/public/token/*`) | Name, symbol, description, creator, image |
| Bonding curve state | `TokenManager2` ABI (on-chain read) | Progress, raised amount, graduation status |
| Token creation args | Four.meme API (`/meme-api/v1/private/token/create`) | For future creator-facing features |
| Buy/sell execution | `TokenManager2` or PancakeSwap router | Trade on bonding curve or DEX |
| Agent identity | `AgentIdentifier` ABI (on-chain write) | Register as ERC-8004 agent wallet |
| Tax token inspection | `TaxToken` ABI (on-chain read) | Check fee parameters for risk scoring |
| Image/metadata | Four.meme CDN URLs | Display token logos in dashboard |

### AI Orchestration

Use AI where it adds judgment. Use deterministic logic where it doesn't.

| Task | Method |
|------|--------|
| Risk signal computation | Deterministic (Web3 reads + math) |
| Score aggregation | Rules engine (weighted scoring) |
| Rationale generation | LLM (Claude API) |
| Token description analysis | LLM (classify as legit/scam/hype) |
| Social sentiment | VADER (lightweight) + LLM (if available) |
| Persona action decision | Rules engine (persona config → action) |
| Transaction building | Deterministic (Web3.py) |
| Override tracking | Deterministic (log + compare) |

**Agent orchestration pattern:**

```
1. Fetch new token data (Four.meme API + on-chain)
2. Compute risk signals (deterministic)
3. Aggregate into score (rules engine)
4. Ask LLM to explain the score and recommend (Claude API)
5. Apply persona rules to filter action
6. If action = buy/sell: build transaction
7. Push to frontend for approval
8. On approval: execute and track
```

---

## 9. Database Schema

```sql
-- Token discoveries
CREATE TABLE tokens (
    address TEXT PRIMARY KEY,
    name TEXT,
    symbol TEXT,
    creator_address TEXT,
    launch_time TEXT,
    risk_score TEXT,           -- green / amber / red
    risk_detail TEXT,          -- JSON: individual signal scores
    risk_rationale TEXT,       -- LLM-generated explanation
    bonding_curve_progress REAL,
    graduated INTEGER DEFAULT 0,
    is_tax_token INTEGER DEFAULT 0,
    last_checked TEXT,
    created_at TEXT
);

-- Scan events
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT,
    scan_type TEXT,            -- new_launch / price_spike / volume_spike / graduation
    risk_score TEXT,
    persona_action TEXT,       -- buy / skip / monitor / exit
    rationale TEXT,
    created_at TEXT
);

-- Active and closed positions
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT,
    entry_price REAL,
    entry_amount_bnb REAL,
    token_quantity REAL,
    current_price REAL,
    status TEXT,               -- active / closed / stopped_out
    exit_price REAL,
    exit_amount_bnb REAL,
    pnl_bnb REAL,
    entry_risk_score TEXT,
    opened_at TEXT,
    closed_at TEXT
);

-- Trade execution log
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER,
    token_address TEXT,
    side TEXT,                 -- buy / sell
    amount_bnb REAL,
    token_quantity REAL,
    price REAL,
    tx_hash TEXT,
    slippage REAL,
    gas_used REAL,
    approval_mode TEXT,        -- manual / auto / threshold
    was_override INTEGER DEFAULT 0,  -- did user override agent recommendation?
    executed_at TEXT
);

-- What I Avoided log
CREATE TABLE avoided (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_address TEXT,
    token_name TEXT,
    risk_score TEXT,
    risk_rationale TEXT,
    price_at_flag REAL,
    price_1h_later REAL,
    price_6h_later REAL,
    price_24h_later REAL,
    confirmed_rug INTEGER DEFAULT 0,
    estimated_savings_bnb REAL,
    flagged_at TEXT
);

-- User configuration
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Watchlist
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT,            -- token / creator / pattern
    value TEXT,
    label TEXT,
    created_at TEXT
);

-- Indexes
CREATE INDEX idx_tokens_creator ON tokens (creator_address);
CREATE INDEX idx_tokens_risk ON tokens (risk_score);
CREATE INDEX idx_scans_token ON scans (token_address);
CREATE INDEX idx_positions_status ON positions (status);
CREATE INDEX idx_avoided_flagged ON avoided (flagged_at);
```

---

## 10. Trust & Safety Controls

| Control | Implementation |
|---------|---------------|
| Spend caps | Hard-coded max per trade / per day / active positions — enforced server-side |
| Token denylist | User can block specific tokens or creators |
| Min liquidity threshold | Agent skips tokens with <$500 liquidity |
| Max slippage guard | Transaction reverts if slippage exceeds user setting |
| Cooldown | Minimum 60s between trades (configurable) |
| Confirm before execution | Always shows full TX preview before signature |
| Session timeout | Auto-lock after 30 min inactivity |
| Private key safety | Never stored in plaintext; encrypted local storage or wallet provider |
| Read-only fallback | Monitor-only mode requires zero on-chain permissions |
| Agent wallet separation | Recommend using a dedicated hot wallet, not main holdings |

---

## 11. Build Order

### Phase 1 — Foundation (Days 1–6)

**Goal:** Working dashboard that shows live Four.meme launches with risk scores.

- [ ] Project scaffolding: FastAPI backend + React/Vite frontend + SQLite
- [ ] BSC Web3 provider setup (Web3.py, BNB testnet + mainnet)
- [ ] Four.meme API client (token list, token detail, bonding curve reads)
- [ ] Wallet connection UI (wagmi + ethers.js)
- [ ] Persona selection page (3 presets with visual cards)
- [ ] Budget cap configuration UI
- [ ] Basic token feed: fetch new launches, display on dashboard
- [ ] Risk scoring engine v1: creator history + holder concentration + liquidity check
- [ ] Token card component with green/amber/red badge

**End of Phase 1 deliverable:** You can open the app, connect wallet, pick a persona, and see a live feed of scored Four.meme tokens.

### Phase 2 — The Brain (Days 7–12)

**Goal:** Agent proposes trades and executes with approval.

- [ ] Complete risk scoring engine: all 8 signals
- [ ] LLM integration (Claude API) for rationale generation
- [ ] Opportunity detail page (full risk breakdown + rationale + action)
- [ ] Persona action engine (rules that map score + persona → action)
- [ ] Transaction builder (buy on bonding curve, sell on PancakeSwap)
- [ ] Approval gate system (4 modes)
- [ ] Transaction preview modal (amount, slippage, gas, approve/reject)
- [ ] Trade execution with wallet signature
- [ ] Activity feed page
- [ ] Position tracking (entry price, current price, PnL)
- [ ] WebSocket for live updates (new opportunities pushed to frontend)

**End of Phase 2 deliverable:** Full trade loop works — agent finds token, scores it, explains it, proposes trade, user approves, trade executes, position tracked.

### Phase 3 — Polish & Demo Features (Days 13–17)

**Goal:** Demo-ready with killer features and visual polish.

- [ ] "What I Avoided" log: background job checks red-flagged tokens at 1h/6h/24h
- [ ] Avoided page UI with savings tally
- [ ] Behavioral nudge: track overrides, show outcome summary
- [ ] Agent wallet ERC-8004 registration (AgentIdentifier contract)
- [ ] Post-trade monitoring: price alerts, momentum loss detection
- [ ] Watchlist page (add tokens, creators, patterns)
- [ ] Dashboard visual polish: dark theme, animations, responsive layout
- [ ] Settings page with all configurable options
- [ ] Demo video recording (3-5 minutes, see demo script below)
- [ ] README with architecture diagram, setup instructions, screenshots
- [ ] GitHub cleanup: .env.example, license, contributing guide

---

## 12. Demo Script (3–4 minutes)

This is the narrative arc a judge will see:

**Scene 1 — Setup (30s)**
Open the app. Connect wallet. Register as ERC-8004 agent (show the on-chain tx — proves Four.meme integration depth). Choose "Momentum" persona. Set 0.5 BNB daily cap. Approve-each mode.

**Scene 2 — Scanning (45s)**
Dashboard lights up with live Four.meme launches. Each token card shows name, launch age, bonding curve progress, and a green/amber/red risk badge. Point out a red-scored token: "This creator launched 3 tokens yesterday — all rugged within 2 hours. Agent automatically flags this."

**Scene 3 — Opportunity (60s)**
Agent highlights a green-scored token. Click into the detail page. Show the full risk breakdown: creator first launch (good sign), healthy holder distribution, strong early volume, no tax token flags. Read the AI-generated rationale: "First-time creator with organic social activity. Volume is consistent, not wash-traded. Momentum persona recommends entry at 0.05 BNB." Click "Approve."

**Scene 4 — Execution (30s)**
Transaction preview shows exact swap details. Sign with wallet. TX confirms on BSC. Position appears in the portfolio view with entry price and live PnL.

**Scene 5 — What I Avoided (45s)**
Switch to the "What I Avoided" tab. Show 4 tokens the agent flagged red earlier in the session. Two have already dropped 90%+. One had liquidity pulled entirely. Running tally: "Avoided 3 confirmed rugs — estimated savings: 0.15 BNB." This is the moment the judge goes "oh, that's useful."

**Scene 6 — Close (15s)**
Back to dashboard. Show the behavioral summary: "1 trade executed. 3 rugs avoided. 0 overrides." End with tagline: "MemeGuard — your AI sentinel for Four.meme."

---

## 13. What Makes This Hackathon-Worthy

A judge evaluating this will see:

| Criterion | How MemeGuard Delivers |
|-----------|----------------------|
| Real problem | Memecoin traders lose money to rugs daily. Information asymmetry on Four.meme is unsolved. |
| Narrow scope | Three capabilities: scan, score, execute. Not trying to be everything. |
| Agentic behavior | Holds wallet, reads market, makes decisions, executes transactions, learns from outcomes. |
| On-chain action | Reads Four.meme contracts, executes swaps on BSC, registers as ERC-8004 agent. |
| Four.meme fit | Built specifically for Four.meme's API, bonding curve, Agentic Mode, and agent identity system. |
| Configurable persona | Three presets with predefined strategies — directly matches AMA guidance. |
| Human oversight | Four approval modes + hard budget caps. User controls the leash. |
| Market awareness | Fear & Greed index, BNB trend, per-token sentiment and on-chain signals. |
| Immediately usable | Open app → connect wallet → pick persona → agent starts working. 2-minute setup. |
| Visual quality | Dark Binance-inspired dashboard, real-time feed, approval modals, portfolio view. |

---

## 14. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Four.meme API changes or goes down | Cache token data, fallback to on-chain reads only |
| LLM latency slows down scoring | Generate rationale async; show score immediately, rationale loads after |
| BSC testnet vs mainnet differences | Develop on testnet, final demo on mainnet with tiny amounts |
| Too many features for solo build | Phase 3 items are nice-to-have; Phase 1+2 alone is a viable submission |
| Private key security concerns | Strong recommendation for dedicated hot wallet; never store keys server-side |

---

## 15. File Structure

```
memeguard/
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Settings, env vars
│   ├── database.py                # SQLite init, schema, queries
│   ├── services/
│   │   ├── scanner.py             # Four.meme API polling + new launch detection
│   │   ├── risk_engine.py         # 8-signal scoring engine
│   │   ├── persona_engine.py      # Persona rules → action mapping
│   │   ├── llm_service.py         # Claude API for rationale generation
│   │   ├── tx_builder.py          # Transaction preparation + preview
│   │   ├── executor.py            # Trade execution (receives signed tx)
│   │   ├── position_tracker.py    # Track open positions, compute PnL
│   │   ├── avoided_tracker.py     # "What I Avoided" background checker
│   │   ├── market_context.py      # Fear & Greed, BNB price, market overview
│   │   └── agent_identity.py      # ERC-8004 registration
│   ├── clients/
│   │   ├── fourmeme_api.py        # Four.meme REST client
│   │   ├── bsc_web3.py            # Web3.py provider + contract interactions
│   │   └── binance_api.py         # Price data, market metrics
│   ├── models/
│   │   ├── token.py               # Token dataclass
│   │   ├── scan.py                # Scan event dataclass
│   │   ├── position.py            # Position dataclass
│   │   └── trade.py               # Trade dataclass
│   ├── abis/
│   │   ├── TokenManager2.json
│   │   ├── AgentIdentifier.json
│   │   ├── TaxToken.json
│   │   └── PancakeRouter.json
│   ├── routes/
│   │   ├── tokens.py              # GET /api/tokens, GET /api/tokens/:address
│   │   ├── actions.py             # POST /api/approve, POST /api/reject
│   │   ├── positions.py           # GET /api/positions
│   │   ├── avoided.py             # GET /api/avoided
│   │   ├── config.py              # GET/PUT /api/config
│   │   ├── watchlist.py           # CRUD /api/watchlist
│   │   └── activity.py            # GET /api/activity
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── OpportunityDetail.jsx
│   │   │   ├── Positions.jsx
│   │   │   ├── Avoided.jsx
│   │   │   ├── Activity.jsx
│   │   │   └── Settings.jsx
│   │   ├── components/
│   │   │   ├── TokenCard.jsx
│   │   │   ├── RiskBadge.jsx
│   │   │   ├── ApprovalModal.jsx
│   │   │   ├── PersonaSelector.jsx
│   │   │   ├── BudgetBar.jsx
│   │   │   ├── PositionRow.jsx
│   │   │   ├── AvoidedCard.jsx
│   │   │   └── Navbar.jsx
│   │   ├── hooks/
│   │   │   ├── useWallet.js
│   │   │   ├── useTokenFeed.js
│   │   │   └── useWebSocket.js
│   │   ├── services/
│   │   │   └── api.js             # Backend API client
│   │   └── styles/
│   │       └── index.css          # Tailwind + custom theme
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## 16. Environment Variables

```env
# BSC
BSC_RPC_URL=https://bsc-dataseed1.binance.org
BSC_TESTNET_RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545
WALLET_PRIVATE_KEY=           # only for agent hot wallet, never main wallet

# Four.meme
FOURMEME_API_BASE=https://four.meme/meme-api/v1

# AI
ANTHROPIC_API_KEY=            # Claude API for rationale generation

# Market Data
BINANCE_API_KEY=              # optional, for enhanced market data
COINGECKO_API_KEY=            # optional, for Fear & Greed

# Contracts (BSC Mainnet)
TOKEN_MANAGER2_ADDRESS=
AGENT_IDENTIFIER_ADDRESS=
PANCAKE_ROUTER_ADDRESS=0x10ED43C718714eb63d5aA57B78B54704E256024E

# App
DATABASE_PATH=./data/memeguard.db
LOG_LEVEL=INFO
SCAN_INTERVAL_SECONDS=30
```

---

## 17. Minimal Viable Demo (If Time Runs Short)

If Phase 3 gets cut, the minimum viable submission is:

- Dashboard with live Four.meme token feed
- Risk scoring with green/amber/red badges
- One persona working (Momentum)
- Transaction preview + approval + execution
- Activity feed showing what the agent did

That alone is a complete agentic product with on-chain action and Four.meme integration. The "What I Avoided" log and behavioral nudge are high-impact polish, not core requirements.

---

*Built for the Four.Meme AI Sprint hackathon. MIT License.*
