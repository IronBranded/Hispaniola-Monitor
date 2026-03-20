# 🇭🇹🇩🇴 Hispaniola Monitor

**Real-time intelligence dashboard for Haiti & the Dominican Republic** — AI-synthesized news, geopolitical monitoring, gang activity tracking, economic signals, and live feeds in a zero-install browser experience.

[![Deploy to GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-blue)](https://pages.github.com)
[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-green)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Live Demo

> Deploy to: `https://YOUR_USERNAME.github.io/hispaniola-monitor`

No installation. No API keys for users. Just open the URL.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Actions (every 6 hours)             │
│  ┌──────────────┐    ┌────────────────┐                 │
│  │ scrape.py    │───▶│ synthesize.py  │◀── Groq API     │
│  │ (435+ feeds) │    │ (AI briefs)    │    (free tier)   │
│  └──────────────┘    └───────┬────────┘                 │
│                              │                          │
│                    intelligence_feed.json               │
│                              │                          │
│                    git push → main                      │
└──────────────────────────────┼──────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────┐
│              GitHub Pages (static hosting)              │
│                                                         │
│  Browser loads intelligence_feed.json                  │
│  ┌──────────────────────────────────────────┐          │
│  │  Hispaniola Monitor Frontend             │          │
│  │  • globe.gl  3D globe                    │          │
│  │  • deck.gl   WebGL flat map              │          │
│  │  • 45 data layers                        │          │
│  │  • Live news feed (Radio Télé Ginen)     │          │
│  │  • Finance radar                         │          │
│  │  • Criminal intelligence index           │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Weekly Email Alert  │
                    │  (Resend free tier) │
                    │  Every Friday 8AM   │
                    └─────────────────────┘
```

---

## Features

### 📡 Intelligence Feed (435+ Sources)
- 15 categories: Politics, Security, Economy, Disaster, Crime, Health, Migration, Energy, Environment, Culture, Sports, Diaspora, Diplomacy, Finance, Infrastructure
- Haiti-specific: Radio sources, Haitian diaspora press, gang tracker RSS
- DR-specific: Listín Diario, Diario Libre, El Caribe, Noticias SIN
- Regional: Caribbean Basin feeds, US State Dept Haiti advisories
- AI brief synthesized every 6 hours via Groq Llama 3.1

### 🗺️ Dual Map Engine
- **globe.gl** — interactive 3D globe with arc layers for migration flows
- **deck.gl** — WebGL flat map with 45 toggleable layers
- Layers include: gang territory zones, checkpoints, UN MINUSTAH/MSS deployment, earthquake zones (Haiti sits on Enriquillo fault), hurricane tracks, IDP camps, border crossing points, hospital locations, cholera outbreak zones

### 🏴‍☠️ Criminal Intelligence Index
- Top 10 active gang leaders in Haiti (G9, G-Pèp, Viv Ansanm coalition)
- Top 10 criminal networks in DR (drug trafficking corridors, Haitian-DR border crime)
- Territory control map updated from BINUH, JILAP, and journalism sources
- Escalation scoring based on incident reports and media velocity

### 📊 Country Intelligence Index (CII)
- Composite risk scoring across 12 signals:
  1. Political stability (government, elections, PM tenure)
  2. Gang/security incidents
  3. Economic distress (inflation, gourde/peso exchange)
  4. Fuel scarcity index
  5. Displacement & IDP counts
  6. Cholera & disease alerts
  7. Natural disaster risk
  8. Border tension signals
  9. Diaspora remittance flow proxy
  10. Media freedom index
  11. UN/international presence
  12. Social unrest velocity

### 💰 Finance Radar
- Haitian companies: UNIBANK, SOGEBANK, Capital Bank, Digicel Haiti, Natcom
- DR-listed companies: Banco Popular, ITLA, EGE Haina, Grupo León Jimenes (E. León)
- Commodities: coffee (Haiti exports), cocoa, sugar (DR exports), rice, oil
- Crypto: BTC/HTG proxy (remittance flows)
- 7-signal market composite: USD/HTG, USD/DOP, remittances, fuel price, bond spreads, FDI proxy, inflation delta

### 📺 Live News Feed
- **Radio Télé Ginen** — embedded live stream (YouTube)
- **Télévision Nationale d'Haïti (TNH)** — official state TV
- **CDN37 (DR)** — Dominican live news
- **AlterPresse** — independent Haitian press RSS
- **Haiti Libre** English RSS

### 📧 Weekly Email Alerts
- Subscribe with email address (stored in Resend audience)
- Every Friday 8 AM EST: synthesized weekly brief
- Covers: top incidents, CII changes, finance movements, criminal activity

---

## Project Structure

```
hispaniola-monitor/
├── .github/
│   └── workflows/
│       ├── scrape.yml          # Runs every 6h — main data pipeline
│       └── weekly-alert.yml    # Runs Fridays — email dispatch
├── scripts/
│   ├── scrape.py               # RSS + API scraper (435+ feeds)
│   ├── synthesize.py           # Groq AI brief generator
│   ├── score_cii.py            # Country Intelligence Index scorer
│   ├── finance.py              # Finance radar data collector
│   ├── criminals.py            # Criminal intelligence updater
│   └── send_alerts.py          # Weekly email dispatch (Resend)
├── src/
│   ├── main.ts                 # Entry point
│   ├── App.tsx                 # Root component
│   ├── components/
│   │   ├── GlobeView.tsx       # globe.gl 3D globe
│   │   ├── MapView.tsx         # deck.gl flat map
│   │   ├── NewsFeed.tsx        # Live scrolling feed
│   │   ├── CIIPanel.tsx        # Country Intelligence Index
│   │   ├── FinanceRadar.tsx    # Finance dashboard
│   │   ├── CriminalIndex.tsx   # Gang/criminal tracker
│   │   ├── LiveStream.tsx      # Embedded TV/radio
│   │   ├── AlertBrief.tsx      # AI-synthesized brief
│   │   └── Subscribe.tsx       # Email subscription
│   ├── data/
│   │   ├── feeds.ts            # All 435+ feed definitions
│   │   ├── layers.ts           # 45 map layer configs
│   │   ├── criminals.ts        # Static criminal intelligence data
│   │   └── baseline.ts         # CII baseline risk weights
│   ├── hooks/
│   │   └── useIntelFeed.ts     # Loads & refreshes intelligence_feed.json
│   └── types/
│       └── index.ts            # TypeScript types
├── public/
│   └── data/
│       └── intelligence_feed.json  # Generated by CI, consumed by browser
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Quick Start (Development)

```bash
git clone https://github.com/YOUR_USERNAME/hispaniola-monitor.git
cd hispaniola-monitor
npm install
npm run dev
```

### Run the data pipeline locally (Home Lab mode with Ollama):
```bash
pip install -r scripts/requirements.txt
# With Ollama (local GPU):
ollama pull llama3.1
python scripts/scrape.py
python scripts/synthesize.py --backend ollama
python scripts/score_cii.py
python scripts/finance.py
# Output: public/data/intelligence_feed.json
```

### Run with Groq (cloud free tier):
```bash
export GROQ_API_KEY=gsk_xxx
python scripts/synthesize.py --backend groq
```

---

## Deployment (Zero-Install)

### 1. Fork & configure secrets
Add to GitHub Secrets:
- `GROQ_API_KEY` — from console.groq.com (free)
- `RESEND_API_KEY` — from resend.com (free tier: 3k emails/month)
- `RESEND_AUDIENCE_ID` — created in Resend dashboard

### 2. Enable GitHub Pages
Settings → Pages → Source: GitHub Actions

### 3. That's it
The workflow runs automatically every 6 hours. Users visit your GitHub Pages URL — no installation, no configuration.

---

## Data Sources

### Haiti News (100+ feeds)
| Source | Language | Tier |
|--------|----------|------|
| AlterPresse | FR/HT | 1 |
| Haiti Libre | EN/FR | 1 |
| Le Nouvelliste | FR | 1 |
| Radio Caraïbes | FR | 2 |
| Haïti en Marche | FR | 2 |
| Rezo Nodwès | HT/FR | 2 |
| Ayibopost | HT/FR | 2 |
| Haiti Observer | EN | 2 |
| Gaillard Center | EN | 3 |
| ... (100+ total) | | |

### DR News (85+ feeds)
| Source | Language | Tier |
|--------|----------|------|
| Listín Diario | ES | 1 |
| Diario Libre | ES | 1 |
| El Caribe | ES | 1 |
| Noticias SIN | ES | 1 |
| CDN 37 | ES | 2 |
| Periódico Hoy | ES | 2 |
| ... (85+ total) | | |

### Regional & International (250+ feeds)
- AP Caribbean desk, Reuters Haiti/DR
- UN OCHA Haiti situation reports
- BINUH press releases
- US State Dept Haiti travel advisories
- OAS, CARICOM, IDB feeds
- World Food Programme Haiti
- MSF Haiti
- ... and more

---

## License

MIT — see LICENSE
