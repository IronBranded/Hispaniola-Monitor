# 🚀 Hispaniola Monitor — Setup Guide

Zero servers. Zero monthly cost. 5-minute deploy.

---

## Step 1 — Fork & Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/hispaniola-monitor.git
cd hispaniola-monitor
```

---

## Step 2 — Get Your Free API Keys (5 minutes)

### 2a. Groq API (AI synthesis — FREE)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up → Create API Key
3. Copy the key starting with `gsk_...`
4. **Free tier**: 30 requests/minute, 14,400/day — more than enough

### 2b. Resend (Email alerts — FREE)
1. Go to [resend.com](https://resend.com)
2. Sign up → API Keys → Create
3. Copy the key starting with `re_...`
4. Go to Audiences → Create Audience → Copy the Audience ID
5. **Free tier**: 3,000 emails/month

---

## Step 3 — Add Secrets to GitHub

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these three secrets:

| Name | Value |
|------|-------|
| `GROQ_API_KEY` | `gsk_xxxxxxxxxxxx` |
| `RESEND_API_KEY` | `re_xxxxxxxxxxxx` |
| `RESEND_AUDIENCE_ID` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |

---

## Step 4 — Enable GitHub Pages

1. Repo → **Settings** → **Pages**
2. Under "Build and deployment" → Source: **GitHub Actions**
3. Save

---

## Step 5 — Trigger First Run

1. Go to **Actions** tab in your repo
2. Click "Intelligence Pipeline"
3. Click "Run workflow" → "Run workflow"
4. Wait ~5 minutes for the first run to complete

Your site will be live at:
```
https://YOUR_USERNAME.github.io/hispaniola-monitor/
```

---

## Step 6 — Update the Subscribe Endpoint

In `index.html`, the subscribe button posts to `/api/subscribe`. 

**Easiest option — Cloudflare Worker (free)**:

```javascript
// workers/subscribe.js
export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('Method not allowed', {status: 405});
    
    const { email } = await request.json();
    if (!email || !email.includes('@')) return new Response('Invalid email', {status: 400});
    
    const res = await fetch(`https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, unsubscribed: false })
    });
    
    if (res.ok) return new Response('{"ok":true}', {headers:{'Content-Type':'application/json'}});
    return new Response('Error', {status: 500});
  }
}
```

Deploy with `wrangler deploy` (free Cloudflare Workers plan).

**Alternative — Vercel Serverless Function** (also free):

Create `api/subscribe.js` in the repo:

```javascript
export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();
  const { email } = req.body;
  
  const response = await fetch(
    `https://api.resend.com/audiences/${process.env.RESEND_AUDIENCE_ID}/contacts`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, unsubscribed: false })
    }
  );
  
  res.status(response.ok ? 200 : 500).json({ ok: response.ok });
}
```

---

## Home Lab Mode (True Ollama — No API Keys)

If you have a GPU workstation, run everything locally and push the feed:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1

# Install Python deps
pip install -r scripts/requirements.txt yfinance

# Add a local cron job (every 6 hours)
crontab -e
# Add:
# 0 0,6,12,18 * * * cd /path/to/hispaniola-monitor && python scripts/scrape.py && python scripts/synthesize.py --backend ollama && python scripts/score_cii.py && python scripts/finance.py && python scripts/criminals.py && python scripts/merge_feed.py && git add public/data/intelligence_feed.json && git commit -m "🔄 Feed update" && git push
```

No GitHub Actions needed. Your local machine does all the compute.

---

## Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| GitHub (hosting + CI) | Free | $0/mo |
| Groq API (AI synthesis) | Free tier | $0/mo |
| Resend (email alerts) | Free tier (3k/mo) | $0/mo |
| Cloudflare Workers (subscribe API) | Free tier | $0/mo |
| **Total** | | **$0/mo** |

---

## Adding the Tauri Desktop App

Once the web app is live, wrapping it in Tauri takes ~30 minutes:

```bash
npm install -g @tauri-apps/cli
npx @tauri-apps/cli init
# In tauri.conf.json, set:
# "devUrl": "https://YOUR_USERNAME.github.io/hispaniola-monitor/"
# "frontendDist": "../dist"
npm run tauri build
```

This produces native `.app` (macOS), `.exe` (Windows), and `.deb/.AppImage` (Linux) installers. The app just points to your GitHub Pages URL — no separate server needed.

---

## Customizing News Sources

Edit `scripts/scrape.py`. The `FEEDS` dictionary has 15 categories. To add a source:

```python
{"url": "https://example.com/rss.xml", "name": "Source Name", "country": "HT", "lang": "FR", "tier": 2}
```

Countries: `HT` (Haiti), `DO` (Dominican Republic), `REGIONAL`, `GLOBAL`  
Tiers: 1 (wire/official), 2 (major outlet), 3 (niche/blog)

---

## Environment Variables Reference

| Variable | Used by | Required |
|----------|---------|----------|
| `GROQ_API_KEY` | `synthesize.py` | Yes (cloud mode) |
| `RESEND_API_KEY` | `send_alerts.py` | Yes (email) |
| `RESEND_AUDIENCE_ID` | `send_alerts.py` | Yes (email) |
| `OUTPUT_DIR` | All scripts | No (default: `public/data`) |

---

## Troubleshooting

**Pipeline fails on scrape.py**  
→ Some feeds may be temporarily down. The script handles failures gracefully — you'll see warnings but it continues.

**No articles in feed**  
→ Check the Actions logs. If feeds are returning empty, try running locally: `python scripts/scrape.py`

**Globe not rendering**  
→ Try a modern browser (Chrome/Firefox). The globe requires WebGL support.

**Email not sending**  
→ Verify `RESEND_API_KEY` and `RESEND_AUDIENCE_ID` in GitHub Secrets. Resend requires a verified sending domain for production.
