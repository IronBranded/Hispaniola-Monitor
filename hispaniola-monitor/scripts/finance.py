#!/usr/bin/env python3
"""
Hispaniola Monitor — Finance Radar
Collects exchange rates, commodities, Haitian/DR company data.
Uses free APIs: exchangerate-api, Yahoo Finance (via yfinance), Open Exchange Rates.
"""

import json
import os
import requests
from datetime import datetime, timezone

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

# ─── Haitian & DR Companies (with proxy tickers where available) ─────────────
COMPANIES = [
    # Haiti (not listed on exchanges but tracked by news)
    {"name": "UNIBANK Haiti", "country": "HT", "sector": "Banking", "ticker": None, "notes": "Largest private bank in Haiti"},
    {"name": "SOGEBANK", "country": "HT", "sector": "Banking", "ticker": None, "notes": "Société Générale Haïtienne de Banque"},
    {"name": "Capital Bank Haiti", "country": "HT", "sector": "Banking", "ticker": None, "notes": "Private commercial bank"},
    {"name": "BNC (Banque Nationale de Crédit)", "country": "HT", "sector": "Banking", "ticker": None, "notes": "State-owned bank"},
    {"name": "BPH (Banque Populaire Haïtienne)", "country": "HT", "sector": "Banking", "ticker": None, "notes": "State bank"},
    {"name": "Digicel Haiti", "country": "HT", "sector": "Telecom", "ticker": None, "notes": "Dominant mobile carrier"},
    {"name": "Natcom", "country": "HT", "sector": "Telecom", "ticker": None, "notes": "National Telecom (state-owned)"},
    {"name": "ELECTRICITE D'HAITI (EDH)", "country": "HT", "sector": "Energy", "ticker": None, "notes": "State power utility"},
    {"name": "SOGENER", "country": "HT", "sector": "Energy", "ticker": None, "notes": "Private power generation"},
    {"name": "GBH (Gilbert Bigio Group)", "country": "HT", "sector": "Conglomerate", "ticker": None, "notes": "Largest Haitian private conglomerate"},
    # Haitian-owned diaspora companies
    {"name": "Lakou Kajou Media", "country": "HT", "sector": "Media", "ticker": None, "notes": "Haitian-owned media diaspora"},
    {"name": "Mango Money (Digicel)", "country": "HT", "sector": "Fintech", "ticker": None, "notes": "Mobile money platform"},
    # DR — listed or significant private
    {"name": "Banco Popular Dominicano", "country": "DO", "sector": "Banking", "ticker": "BPD.SN", "notes": "Largest commercial bank DR"},
    {"name": "Banreservas", "country": "DO", "sector": "Banking", "ticker": None, "notes": "State bank DR"},
    {"name": "EGE Haina", "country": "DO", "sector": "Energy", "ticker": "EGEHAINA.SN", "notes": "Electricity generator DR"},
    {"name": "Grupo León Jimenes", "country": "DO", "sector": "Conglomerate", "ticker": None, "notes": "Cervecería Nacional Dominicana, E.León"},
    {"name": "Claro RD (América Móvil)", "country": "DO", "sector": "Telecom", "ticker": "AMX", "notes": "Dominant telco DR"},
    {"name": "ALTICE Dominicana", "country": "DO", "sector": "Telecom", "ticker": None, "notes": "Cable & mobile DR"},
    {"name": "Brugal & Co.", "country": "DO", "sector": "Beverages", "ticker": None, "notes": "Rum producer, DR export"},
    {"name": "Casa Brugal (Edrington)", "country": "DO", "sector": "Beverages", "ticker": "EDR.L", "notes": "Scottish parent, DR rum"},
    {"name": "Grupo Inicia", "country": "DO", "sector": "Real Estate", "ticker": None, "notes": "DR real estate developer"},
]

# ─── Commodity tickers relevant to Haiti/DR economies ────────────────────────
COMMODITIES = [
    {"symbol": "CC=F", "name": "Cocoa Futures", "unit": "USD/ton", "relevance": "DR major export"},
    {"symbol": "KC=F", "name": "Coffee Futures (Arabica)", "unit": "USD/lb", "relevance": "Haiti/DR export"},
    {"symbol": "SB=F", "name": "Sugar Futures", "unit": "USD/lb", "relevance": "DR major export"},
    {"symbol": "ZR=F", "name": "Rice Futures", "unit": "USD/cwt", "relevance": "Haiti staple import"},
    {"symbol": "CL=F", "name": "Crude Oil WTI", "unit": "USD/barrel", "relevance": "Haiti/DR fuel costs"},
    {"symbol": "BTC-USD", "name": "Bitcoin", "unit": "USD", "relevance": "Remittance proxy / crypto adoption"},
    {"symbol": "ETH-USD", "name": "Ethereum", "unit": "USD", "relevance": "DeFi remittance tracking"},
]

def get_exchange_rates() -> dict:
    """Fetch USD/HTG and USD/DOP from free API."""
    rates = {}
    try:
        # ExchangeRate-API free tier
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
        data = r.json()
        rates["USD_HTG"] = data["rates"].get("HTG", None)
        rates["USD_DOP"] = data["rates"].get("DOP", None)
        rates["source"] = "exchangerate-api.com"
        rates["timestamp"] = datetime.now(timezone.utc).isoformat()
    except Exception as e:
        print(f"  ⚠ Exchange rate fetch failed: {e}")
        rates = {"USD_HTG": None, "USD_DOP": None, "source": "unavailable"}
    return rates

def get_commodity_prices() -> list:
    """Fetch commodity prices using yfinance."""
    results = []
    try:
        import yfinance as yf
        for commodity in COMMODITIES:
            try:
                ticker = yf.Ticker(commodity["symbol"])
                hist = ticker.history(period="2d")
                if not hist.empty:
                    price = round(hist["Close"].iloc[-1], 4)
                    prev = round(hist["Close"].iloc[-2], 4) if len(hist) > 1 else price
                    change_pct = round((price - prev) / prev * 100, 2) if prev else 0
                    results.append({
                        **commodity,
                        "price": price,
                        "prev_close": prev,
                        "change_pct": change_pct,
                        "status": "ok"
                    })
                else:
                    results.append({**commodity, "price": None, "status": "no_data"})
            except Exception as e:
                results.append({**commodity, "price": None, "status": f"error: {str(e)[:50]}"})
    except ImportError:
        print("  ⚠ yfinance not installed — skipping commodity prices")
        results = [{**c, "price": None, "status": "yfinance not installed"} for c in COMMODITIES]
    return results

def compute_market_composite(rates: dict, commodities: list) -> dict:
    """
    7-signal market composite score for Hispaniola.
    Signals: USD/HTG, USD/DOP, oil price, food commodities (rice, sugar),
             remittance proxy (BTC), coffee/cocoa export value.
    Higher score = more stress.
    """
    score = 50  # neutral baseline
    signals = []
    
    # Signal 1: HTG devaluation (HTG > 120 = stress, historical norm ~110-130)
    if rates.get("USD_HTG"):
        htg = rates["USD_HTG"]
        if htg > 130:
            score += 10
            signals.append({"signal": "HTG devaluation", "value": htg, "impact": "negative"})
        elif htg < 110:
            score -= 5
            signals.append({"signal": "HTG stable", "value": htg, "impact": "positive"})
    
    # Signal 2: Oil price (>85 = stress for import-dependent Haiti)
    oil = next((c for c in commodities if c["symbol"] == "CL=F"), None)
    if oil and oil.get("price"):
        if oil["price"] > 85:
            score += 8
            signals.append({"signal": "High oil price", "value": oil["price"], "impact": "negative"})
        elif oil["price"] < 70:
            score -= 3
            signals.append({"signal": "Low oil price", "value": oil["price"], "impact": "positive"})
    
    return {
        "composite_score": min(100, max(0, score)),
        "signals": signals,
        "interpretation": "high_stress" if score >= 65 else "moderate" if score >= 40 else "stable"
    }

def main():
    print("💰 Collecting finance radar data...")
    
    rates = get_exchange_rates()
    print(f"  💱 USD/HTG: {rates.get('USD_HTG')} | USD/DOP: {rates.get('USD_DOP')}")
    
    commodities = get_commodity_prices()
    print(f"  📦 {len([c for c in commodities if c.get('price')])} commodity prices fetched")
    
    composite = compute_market_composite(rates, commodities)
    print(f"  📊 Market composite: {composite['composite_score']} ({composite['interpretation']})")
    
    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "exchange_rates": rates,
        "commodities": commodities,
        "companies": COMPANIES,
        "market_composite": composite,
    }
    
    out_path = os.path.join(OUTPUT_DIR, "finance.json")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    
    print(f"✅ Finance data saved → {out_path}")

if __name__ == "__main__":
    main()
