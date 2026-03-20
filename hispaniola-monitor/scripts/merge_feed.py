#!/usr/bin/env python3
"""
Hispaniola Monitor — Feed Merger
Combines all pipeline outputs into a single intelligence_feed.json.
"""

import json
import os
from datetime import datetime, timezone

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

def load_json(filename: str) -> dict:
    path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  ⚠ {filename} not found — using empty placeholder")
        return {}

def main():
    print("🔗 Merging all data into intelligence_feed.json...")
    
    raw = load_json("raw_articles.json")
    synthesis = load_json("synthesis.json")
    cii = load_json("cii.json")
    finance = load_json("finance.json")
    criminals = load_json("criminals.json")
    
    # Recent articles: last 200, sorted newest first
    articles = raw.get("articles", [])[:200]
    
    feed = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "project": "hispaniola-monitor",
            "total_articles": len(articles),
            "total_feeds_scraped": raw.get("total_feeds", 0),
            "scrape_time": raw.get("scraped_at"),
        },
        "executive_summary": synthesis.get("executive_summary", ""),
        "category_briefs": synthesis.get("category_briefs", {}),
        "articles": articles,
        "cii": cii.get("countries", {}),
        "finance": {
            "exchange_rates": finance.get("exchange_rates", {}),
            "commodities": finance.get("commodities", []),
            "companies": finance.get("companies", []),
            "market_composite": finance.get("market_composite", {}),
        },
        "criminal_intelligence": {
            "haiti": criminals.get("haiti", {}),
            "dominican_republic": criminals.get("dominican_republic", {}),
        },
        "live_streams": [
            {
                "name": "Radio Télé Ginen",
                "country": "HT",
                "type": "youtube_live",
                "url": "https://www.youtube.com/@RadioTeleGinen/live",
                "embed_id": None,  # Update with actual YouTube channel live ID
                "language": "HT/FR",
                "description": "Haiti's popular independent radio and TV network",
            },
            {
                "name": "TNH — Télévision Nationale d'Haïti",
                "country": "HT",
                "type": "youtube_live",
                "url": "https://www.youtube.com/@TNH/live",
                "embed_id": None,
                "language": "FR/HT",
                "description": "Official Haitian state television",
            },
            {
                "name": "CDN 37 — Dominicana",
                "country": "DO",
                "type": "youtube_live",
                "url": "https://www.youtube.com/@CDN37/live",
                "embed_id": None,
                "language": "ES",
                "description": "Dominican Republic news channel",
            },
            {
                "name": "SIN Live",
                "country": "DO",
                "type": "youtube_live",
                "url": "https://www.youtube.com/@NoticiasSIN/live",
                "embed_id": None,
                "language": "ES",
                "description": "Noticias SIN live stream",
            },
        ],
        "map_data": {
            "gang_territories": _get_gang_territories(criminals),
            "crisis_points": _get_crisis_points(articles),
            "border_crossings": _get_border_crossings(),
            "key_infrastructure": _get_infrastructure(),
        }
    }
    
    out_path = os.path.join(OUTPUT_DIR, "intelligence_feed.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, separators=(',', ':'))
    
    size_kb = os.path.getsize(out_path) / 1024
    print(f"✅ intelligence_feed.json → {out_path} ({size_kb:.1f} KB)")

def _get_gang_territories(criminals: dict) -> list:
    territories = []
    for c in criminals.get("haiti", {}).get("criminals", []):
        if c.get("coordinates") and c.get("status") == "active":
            territories.append({
                "name": c["alias"] or c["name"],
                "organization": c["organization"],
                "lat": c["coordinates"][0],
                "lng": c["coordinates"][1],
                "threat_level": c["threat_level"],
                "country": "HT",
                "type": "gang_presence",
            })
    for c in criminals.get("dominican_republic", {}).get("criminals", []):
        if c.get("coordinates") and c.get("status") in ["active", "emerging"]:
            territories.append({
                "name": c["alias"] or c["name"],
                "organization": c["organization"],
                "lat": c["coordinates"][0],
                "lng": c["coordinates"][1],
                "threat_level": c["threat_level"],
                "country": "DO",
                "type": "criminal_network",
            })
    return territories

def _get_crisis_points(articles: list) -> list:
    """Extract geotagged crisis signals from articles."""
    # Simplified: use known location keywords
    LOCATIONS = {
        "Port-au-Prince": [18.5432, -72.3395],
        "Cap-Haïtien": [19.7575, -72.2083],
        "Cité Soleil": [18.5792, -72.3288],
        "Artibonite": [19.2000, -72.7000],
        "Jérémie": [18.6431, -74.1165],
        "Les Cayes": [18.2007, -73.7511],
        "Gonaïves": [19.4482, -72.6831],
        "Saint-Marc": [19.1067, -72.6900],
        "Jacmel": [18.2338, -72.5351],
        "Santo Domingo": [18.4861, -69.9312],
        "Santiago DR": [19.4517, -70.6970],
        "Dajabón": [19.5558, -71.7054],
        "Jimaní": [18.4956, -71.8497],
        "Malpasse": [18.7736, -71.9531],
    }
    
    points = []
    seen = set()
    for article in articles[:50]:
        text = article.get("title", "") + " " + article.get("summary", "")
        for loc, coords in LOCATIONS.items():
            if loc.lower() in text.lower() and loc not in seen:
                seen.add(loc)
                points.append({
                    "location": loc,
                    "lat": coords[0],
                    "lng": coords[1],
                    "article_count": sum(1 for a in articles if loc.lower() in (a.get("title","") + a.get("summary","")).lower()),
                    "latest_headline": article["title"],
                    "country": "HT" if coords[1] < -71.5 else "DO",
                })
    return points

def _get_border_crossings() -> list:
    return [
        {"name": "Dajabón / Ouanaminthe", "lat": 19.5558, "lng": -71.7054, "status": "monitored", "type": "official"},
        {"name": "Elías Piña / Belladère", "lat": 18.8839, "lng": -71.6917, "status": "monitored", "type": "official"},
        {"name": "Jimaní / Malpasse", "lat": 18.4956, "lng": -71.8497, "status": "monitored", "type": "official"},
        {"name": "Pedernales / Anse-à-Pitres", "lat": 18.0377, "lng": -71.7456, "status": "limited", "type": "official"},
    ]

def _get_infrastructure() -> list:
    return [
        {"name": "Port-au-Prince Port", "lat": 18.5489, "lng": -72.3430, "type": "port", "country": "HT", "strategic": True},
        {"name": "Cap-Haïtien Port", "lat": 19.7525, "lng": -72.2017, "type": "port", "country": "HT", "strategic": True},
        {"name": "Toussaint Louverture Airport", "lat": 18.5799, "lng": -72.2925, "type": "airport", "country": "HT", "strategic": True},
        {"name": "Hugo Chávez Airport (CAP)", "lat": 19.7330, "lng": -72.1941, "type": "airport", "country": "HT", "strategic": False},
        {"name": "Las Américas Airport (SDQ)", "lat": 18.4297, "lng": -69.6688, "type": "airport", "country": "DO", "strategic": True},
        {"name": "Port of Caucedo (DR)", "lat": 18.4069, "lng": -69.6264, "type": "port", "country": "DO", "strategic": True},
        {"name": "ENCO Fuel Terminal Varreux", "lat": 18.5605, "lng": -72.3320, "type": "fuel_terminal", "country": "HT", "strategic": True},
        {"name": "Peligre Dam (EDH)", "lat": 19.0131, "lng": -72.0328, "type": "hydro_dam", "country": "HT", "strategic": True},
    ]

if __name__ == "__main__":
    main()
