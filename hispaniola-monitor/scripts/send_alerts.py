#!/usr/bin/env python3
"""
Hispaniola Monitor — Weekly Email Alert
Sends synthesized intelligence brief to subscribers via Resend.
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID")
FEED_URL = os.environ.get("FEED_URL", "https://raw.githubusercontent.com/YOUR_USERNAME/hispaniola-monitor/main/public/data/intelligence_feed.json")
FROM_EMAIL = "alerts@hispaniola-monitor.dev"
FROM_NAME = "Hispaniola Monitor"

def fetch_feed() -> dict:
    r = requests.get(FEED_URL, timeout=15)
    return r.json()

def get_subscribers() -> list:
    """Fetch subscriber list from Resend audience."""
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}"}
    r = requests.get(f"https://api.resend.com/audiences/{RESEND_AUDIENCE_ID}/contacts", headers=headers)
    if r.status_code == 200:
        contacts = r.json().get("data", [])
        return [c["email"] for c in contacts if not c.get("unsubscribed", False)]
    return []

def build_email_html(feed: dict) -> tuple[str, str]:
    """Build HTML and text versions of the weekly brief."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")
    
    executive = feed.get("executive_summary", "No summary available.")
    briefs = feed.get("category_briefs", {})
    cii = feed.get("cii", {})
    finance = feed.get("finance", {})
    
    ht_cii = cii.get("HT", {})
    do_cii = cii.get("DO", {})
    rates = finance.get("exchange_rates", {})
    
    risk_color = {"critical": "#dc2626", "high": "#ea580c", "medium": "#d97706", "low": "#16a34a"}
    
    ht_color = risk_color.get(ht_cii.get("risk_level", "medium"), "#d97706")
    do_color = risk_color.get(do_cii.get("risk_level", "low"), "#16a34a")
    
    top_articles = feed.get("articles", [])[:5]
    article_html = "".join([
        f'<li style="margin-bottom:8px;"><a href="{a["url"]}" style="color:#3b82f6;">{a["title"]}</a> <span style="color:#9ca3af;font-size:12px;">— {a["source"]}</span></li>'
        for a in top_articles
    ])
    
    priority_briefs = {k: v for k, v in briefs.items() if k in ["security", "politics", "economy", "disaster"]}
    briefs_html = "".join([
        f'<div style="margin-bottom:16px;"><strong style="color:#e2e8f0;text-transform:uppercase;font-size:11px;letter-spacing:1px;">{cat}</strong><p style="color:#cbd5e1;margin:4px 0 0;">{brief}</p></div>'
        for cat, brief in priority_briefs.items() if brief
    ])
    
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="background:#0f172a;color:#e2e8f0;font-family:monospace;max-width:640px;margin:0 auto;padding:24px;">
  <div style="border-bottom:1px solid #334155;margin-bottom:24px;padding-bottom:16px;">
    <div style="color:#ef4444;font-size:11px;letter-spacing:2px;margin-bottom:4px;">🇭🇹🇩🇴 HISPANIOLA MONITOR</div>
    <h1 style="margin:0;font-size:20px;color:#f1f5f9;">Weekly Intelligence Brief</h1>
    <div style="color:#64748b;font-size:12px;margin-top:4px;">{date_str} | Compiled every Friday 08:00 EST</div>
  </div>
  
  <div style="background:#1e293b;border-left:3px solid #ef4444;padding:16px;margin-bottom:24px;">
    <div style="color:#94a3b8;font-size:11px;letter-spacing:1px;margin-bottom:8px;">EXECUTIVE SUMMARY</div>
    <p style="margin:0;color:#e2e8f0;line-height:1.6;">{executive}</p>
  </div>
  
  <div style="display:flex;gap:16px;margin-bottom:24px;">
    <div style="flex:1;background:#1e293b;padding:16px;border-top:3px solid {ht_color};">
      <div style="color:#94a3b8;font-size:11px;">🇭🇹 HAITI CII</div>
      <div style="font-size:28px;font-weight:bold;color:{ht_color};">{ht_cii.get('composite_score', 'N/A')}</div>
      <div style="color:#64748b;font-size:12px;">{ht_cii.get('risk_level', '').upper()} RISK</div>
    </div>
    <div style="flex:1;background:#1e293b;padding:16px;border-top:3px solid {do_color};">
      <div style="color:#94a3b8;font-size:11px;">🇩🇴 DR CII</div>
      <div style="font-size:28px;font-weight:bold;color:{do_color};">{do_cii.get('composite_score', 'N/A')}</div>
      <div style="color:#64748b;font-size:12px;">{do_cii.get('risk_level', '').upper()} RISK</div>
    </div>
    <div style="flex:1;background:#1e293b;padding:16px;border-top:3px solid #3b82f6;">
      <div style="color:#94a3b8;font-size:11px;">💱 RATES</div>
      <div style="color:#e2e8f0;font-size:13px;">HTG: {rates.get('USD_HTG', 'N/A')}</div>
      <div style="color:#e2e8f0;font-size:13px;">DOP: {rates.get('USD_DOP', 'N/A')}</div>
    </div>
  </div>
  
  <div style="margin-bottom:24px;">
    <div style="color:#94a3b8;font-size:11px;letter-spacing:1px;margin-bottom:12px;">INTELLIGENCE BRIEFS</div>
    {briefs_html}
  </div>
  
  <div style="margin-bottom:24px;">
    <div style="color:#94a3b8;font-size:11px;letter-spacing:1px;margin-bottom:12px;">TOP STORIES</div>
    <ul style="padding-left:20px;margin:0;">{article_html}</ul>
  </div>
  
  <div style="border-top:1px solid #334155;padding-top:16px;text-align:center;">
    <a href="https://YOUR_USERNAME.github.io/hispaniola-monitor" style="color:#3b82f6;">Open Dashboard →</a>
    <div style="color:#475569;font-size:11px;margin-top:8px;">
      You're receiving this because you subscribed to Hispaniola Monitor alerts.<br>
      <a href="{{{{unsubscribe}}}}" style="color:#475569;">Unsubscribe</a>
    </div>
  </div>
</body>
</html>"""
    
    subject = f"🇭🇹🇩🇴 Hispaniola Monitor — Weekly Brief {date_str}"
    return subject, html

def send_email(to_email: str, subject: str, html: str) -> bool:
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": [to_email],
        "subject": subject,
        "html": html,
    }
    r = requests.post("https://api.resend.com/emails", headers=headers, json=payload)
    return r.status_code == 200

def main():
    if not RESEND_API_KEY:
        print("ERROR: RESEND_API_KEY not set")
        sys.exit(1)
    
    print("📧 Sending weekly intelligence brief...")
    
    feed = fetch_feed()
    print(f"  ✓ Feed loaded ({feed['meta']['total_articles']} articles)")
    
    subject, html = build_email_html(feed)
    print(f"  ✓ Email built: {subject}")
    
    subscribers = get_subscribers()
    print(f"  ✓ {len(subscribers)} subscribers")
    
    sent = 0
    for email in subscribers:
        if send_email(email, subject, html):
            sent += 1
        else:
            print(f"  ⚠ Failed to send to {email}")
    
    print(f"✅ Sent to {sent}/{len(subscribers)} subscribers")

def add_subscriber(email: str) -> bool:
    """Add a subscriber to the Resend audience (called from frontend via separate serverless function)."""
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"email": email, "unsubscribed": False}
    r = requests.post(f"https://api.resend.com/audiences/{RESEND_AUDIENCE_ID}/contacts", 
                       headers=headers, json=payload)
    return r.status_code in [200, 201]

if __name__ == "__main__":
    main()
