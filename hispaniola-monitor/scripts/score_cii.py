#!/usr/bin/env python3
"""
Hispaniola Monitor — Country Intelligence Index (CII) Scorer
Computes composite risk score across 12 signals for Haiti and DR.
"""

import json
import os
import re
from datetime import datetime, timezone
from collections import Counter

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

# ─── Baseline risk weights (0–100) ──────────────────────────────────────────
BASELINE = {
    "HT": {
        "political_stability": 72,   # Haiti: very high baseline instability
        "gang_security": 85,
        "economic_distress": 78,
        "fuel_scarcity": 70,
        "displacement_idp": 75,
        "disease_health": 65,
        "natural_disaster": 60,      # Enriquillo fault, hurricanes
        "border_tension": 55,
        "diaspora_remittance": 30,   # lower = better (remittances help)
        "media_freedom": 55,
        "international_presence": 35,# lower = more international help present
        "social_unrest_velocity": 70,
    },
    "DO": {
        "political_stability": 25,
        "gang_security": 30,
        "economic_distress": 28,
        "fuel_scarcity": 20,
        "displacement_idp": 15,
        "disease_health": 20,
        "natural_disaster": 35,
        "border_tension": 45,        # Haiti border pressure
        "diaspora_remittance": 20,
        "media_freedom": 30,
        "international_presence": 15,
        "social_unrest_velocity": 25,
    }
}

# ─── Keyword signal detectors ────────────────────────────────────────────────
SIGNAL_KEYWORDS = {
    "gang_security": ["gang", "gang", "kidnapping", "kidnap", "armed group", "bandits", "bandi",
                       "G9", "G-Pèp", "Viv Ansanm", "Jimmy Chérizier", "Barbecue", "Vitelhomme",
                       "Ti Gabriel", "Chen Mechan", "Kraze Baryè", "shooting", "massacre",
                       "assassination", "barricade", "arson", "pillage", "armed attack"],
    "political_stability": ["prime minister", "premier ministre", "president", "coup", "election",
                             "resignation", "arrested", "parliament", "senat", "conseil présidentiel",
                             "CPT", "transition", "interim", "instability", "crisis", "manifesto"],
    "economic_distress": ["gourde", "inflation", "hunger", "famine", "shortage", "pénurie",
                           "unemployment", "chômage", "remittance", "poverty", "pauvreté",
                           "exchange rate", "devaluation", "price hike"],
    "fuel_scarcity": ["fuel", "essence", "carburant", "gas shortage", "pénurie d'essence",
                       "black market", "marché noir", "gas station", "ENCO", "EDH"],
    "displacement_idp": ["displaced", "IDP", "déplacé", "flee", "fuir", "evacuation", "évacuation",
                          "refugee", "réfugié", "camp", "shelter", "abri"],
    "disease_health": ["cholera", "choléra", "outbreak", "épidémie", "malaria", "COVID",
                        "hospital", "hôpital", "MSF", "WHO", "vaccination", "health crisis"],
    "natural_disaster": ["earthquake", "séisme", "tremblement", "hurricane", "ouragan",
                          "flood", "inondation", "storm", "tropical", "landslide", "glissement",
                          "Enriquillo", "USGS", "tsunami"],
    "border_tension": ["border", "frontière", "deportation", "expulsion", "migration",
                        "crossing", "crossing point", "Dajabón", "Malpasse", "Ouanaminthe"],
    "social_unrest_velocity": ["protest", "manifestation", "strike", "grève", "demonstration",
                                 "mobilization", "barricade", "roadblock", "blokis"],
}

def count_signals(articles: list, keywords: list, country_filter: str = None) -> int:
    count = 0
    for a in articles:
        if country_filter and a.get("country") not in [country_filter, "REGIONAL", "GLOBAL"]:
            continue
        text = (a.get("title", "") + " " + a.get("summary", "")).lower()
        if any(kw.lower() in text for kw in keywords):
            count += 1
    return count

def compute_cii(country: str, articles: list) -> dict:
    base = BASELINE[country].copy()
    scores = {}
    signal_counts = {}
    
    for signal, keywords in SIGNAL_KEYWORDS.items():
        count = count_signals(articles, keywords, country)
        signal_counts[signal] = count
        
        # Dynamic boost: each matching article adds up to 15 points above baseline
        boost = min(count * 3, 20)
        scores[signal] = min(100, base.get(signal, 30) + boost)
    
    # Fill in non-keyword signals from baseline
    for signal in base:
        if signal not in scores:
            scores[signal] = base[signal]
    
    # Weighted composite
    weights = {
        "gang_security": 0.18,
        "political_stability": 0.15,
        "economic_distress": 0.12,
        "displacement_idp": 0.10,
        "fuel_scarcity": 0.09,
        "social_unrest_velocity": 0.09,
        "natural_disaster": 0.08,
        "border_tension": 0.07,
        "disease_health": 0.07,
        "media_freedom": 0.02,
        "diaspora_remittance": 0.02,
        "international_presence": 0.01,
    }
    
    composite = sum(scores.get(s, 50) * w for s, w in weights.items())
    
    # Trend: compare to previous (simplified)
    trend = "stable"
    if composite > 65:
        trend = "deteriorating"
    elif composite < 35:
        trend = "improving"
    
    return {
        "country": country,
        "composite_score": round(composite, 1),
        "risk_level": "critical" if composite >= 70 else "high" if composite >= 50 else "medium" if composite >= 30 else "low",
        "trend": trend,
        "signals": scores,
        "signal_article_counts": signal_counts,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }

def main():
    print("📊 Computing Country Intelligence Index...")
    
    raw_path = os.path.join(OUTPUT_DIR, "raw_articles.json")
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)
    articles = data["articles"]
    
    cii_haiti = compute_cii("HT", articles)
    cii_dr = compute_cii("DO", articles)
    
    print(f"  🇭🇹 Haiti CII: {cii_haiti['composite_score']} ({cii_haiti['risk_level']})")
    print(f"  🇩🇴 DR CII:    {cii_dr['composite_score']} ({cii_dr['risk_level']})")
    
    out = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "countries": {
            "HT": cii_haiti,
            "DO": cii_dr,
        }
    }
    
    out_path = os.path.join(OUTPUT_DIR, "cii.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    
    print(f"✅ CII saved → {out_path}")

if __name__ == "__main__":
    main()
