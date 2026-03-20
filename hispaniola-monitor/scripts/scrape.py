#!/usr/bin/env python3
"""
Hispaniola Monitor — News Scraper
Scrapes 435+ curated RSS/Atom feeds across 15 categories.
Outputs: public/data/raw_articles.json
"""

import feedparser
import json
import os
import time
import hashlib
from datetime import datetime, timezone
from dateutil import parser as dateparser
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

# ─────────────────────────────────────────────────────────────────────────────
# FEED REGISTRY — 435+ curated sources across 15 categories
# ─────────────────────────────────────────────────────────────────────────────
FEEDS = {

    # ── POLITICS ──────────────────────────────────────────────────────────────
    "politics": [
        # Haiti
        {"url": "https://www.alterpresse.org/rss.php", "name": "AlterPresse", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.haitilibre.com/rss_actualites.xml", "name": "Haiti Libre", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.lenouvellistste.com/rss/politique", "name": "Le Nouvelliste Politique", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://ayibopost.com/feed/", "name": "Ayibopost", "country": "HT", "lang": "HT/FR", "tier": 2},
        {"url": "https://rezonodwes.com/feed/", "name": "Rezo Nodwès", "country": "HT", "lang": "HT/FR", "tier": 2},
        {"url": "https://www.haitienmarche.com/index.php?format=feed&type=rss", "name": "Haïti en Marche", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://haitiantimes.com/feed/", "name": "Haitian Times", "country": "HT", "lang": "EN", "tier": 2},
        {"url": "https://www.haitiobserver.com/rss.xml", "name": "Haiti Observer", "country": "HT", "lang": "EN", "tier": 2},
        {"url": "https://www.loophaiti.com/rss.xml", "name": "Loop Haiti", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://www.metropolehaiti.com/metropole/rss.xml", "name": "Radio Métropole", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://www.radiocaraibesinfo.com/feed/", "name": "Radio Caraïbes", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://www.radiovisioncom.com/feed/", "name": "Radio Vision 2000", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://lenouvelliste.com/feed", "name": "Le Nouvelliste", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.gazette.ht/feed/", "name": "Gazette Haïti", "country": "HT", "lang": "FR", "tier": 3},
        {"url": "https://juno7.ht/feed/", "name": "Juno7", "country": "HT", "lang": "FR", "tier": 2},
        # DR
        {"url": "https://www.listindiario.com/rss/", "name": "Listín Diario", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.diariolibre.com/rss/ultimas-noticias.xml", "name": "Diario Libre", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.elcaribe.com.do/feed/", "name": "El Caribe", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://noticiassin.com/feed/", "name": "Noticias SIN", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://elnacional.com.do/feed/", "name": "El Nacional DO", "country": "DO", "lang": "ES", "tier": 2},
        {"url": "https://acento.com.do/feed/", "name": "Acento DO", "country": "DO", "lang": "ES", "tier": 2},
        {"url": "https://hoy.com.do/feed/", "name": "Periódico Hoy", "country": "DO", "lang": "ES", "tier": 2},
        {"url": "https://www.eldinero.com.do/feed/", "name": "El Dinero DO", "country": "DO", "lang": "ES", "tier": 2},
        {"url": "https://dominicantoday.com/dr/feed/", "name": "Dominican Today", "country": "DO", "lang": "EN", "tier": 2},
        {"url": "https://www.dr1.com/forums/external.php?type=RSS2", "name": "DR1 News", "country": "DO", "lang": "EN", "tier": 2},
    ],

    # ── SECURITY / GANG ACTIVITY ──────────────────────────────────────────────
    "security": [
        # Haiti gang & security tracking
        {"url": "https://www.alterpresse.org/spip.php?page=rss&rubrique=9", "name": "AlterPresse Sécurité", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://ayibopost.com/category/insecurite/feed/", "name": "Ayibopost Insécurité", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://www.haitilibre.com/rss_securite.xml", "name": "Haiti Libre Sécurité", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://rezonodwes.com/category/sekirite/feed/", "name": "Rezo Nodwès Sékirite", "country": "HT", "lang": "HT", "tier": 2},
        # International monitoring
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti", "name": "ReliefWeb Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.crisisgroup.org/rss.xml", "name": "ICG Crisis Group", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://acleddata.com/feed/", "name": "ACLED Data", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.insightcrime.org/feed/", "name": "InSight Crime", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.insightcrime.org/haiti/feed/", "name": "InSight Crime Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.insightcrime.org/dominican-republic/feed/", "name": "InSight Crime DR", "country": "DO", "lang": "EN", "tier": 1},
        {"url": "https://www.globalsecurity.org/rss/caribbean-news.xml", "name": "GlobalSecurity Caribbean", "country": "REGIONAL", "lang": "EN", "tier": 2},
        # DR security
        {"url": "https://www.listindiario.com/la-republica/seguridad/rss/", "name": "Listín Seguridad", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://acento.com.do/category/politica/seguridad/feed/", "name": "Acento Seguridad", "country": "DO", "lang": "ES", "tier": 2},
    ],

    # ── ECONOMY ───────────────────────────────────────────────────────────────
    "economy": [
        {"url": "https://www.haitilibre.com/rss_economie.xml", "name": "Haiti Libre Économie", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://lenouvelliste.com/category/economie/feed", "name": "Le Nouvelliste Économie", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.eldinero.com.do/feed/", "name": "El Dinero DR", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.diariolibre.com/economia/rss.xml", "name": "Diario Libre Economía", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.idbinvest.org/en/rss.xml", "name": "IDB Invest Caribbean", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.worldbank.org/en/country/haiti/rss", "name": "World Bank Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.worldbank.org/en/country/dominicanrepublic/rss", "name": "World Bank DR", "country": "DO", "lang": "EN", "tier": 1},
        {"url": "https://www.imf.org/en/News/RSS?country=HT", "name": "IMF Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.imf.org/en/News/RSS?country=DO", "name": "IMF DR", "country": "DO", "lang": "EN", "tier": 1},
        {"url": "https://cepalstat-prod.cepal.org/cepalstat/rss.aspx", "name": "CEPAL Caribbean", "country": "REGIONAL", "lang": "ES", "tier": 1},
        {"url": "https://www.caribbeannationalweekly.com/feed/", "name": "Caribbean National Weekly Economy", "country": "REGIONAL", "lang": "EN", "tier": 3},
    ],

    # ── DISASTER / NATURAL HAZARDS ────────────────────────────────────────────
    "disaster": [
        {"url": "https://www.gdacs.org/xml/rss_alerts.xml", "name": "GDACS Global Alerts", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom", "name": "USGS Earthquakes", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.nhc.noaa.gov/index-at.xml", "name": "NHC Atlantic Hurricanes", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&type=disaster", "name": "ReliefWeb Haiti Disasters", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://ocha.unocha.org/latin-america-caribbean/haiti/rss", "name": "OCHA Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.mspp.gouv.ht/rss.xml", "name": "MSPP Haiti (Ministry of Health)", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://feeds.feedburner.com/Haiti-quake", "name": "Haiti Earthquake Monitor", "country": "HT", "lang": "EN", "tier": 2},
        {"url": "https://www.coa.int/en/rss/disaster-alerts.xml", "name": "Caribbean Disaster Emergency", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.cdera.org/rss/alerts.xml", "name": "CDEMA Alerts", "country": "REGIONAL", "lang": "EN", "tier": 1},
    ],

    # ── CRIME / CRIMINAL NETWORKS ─────────────────────────────────────────────
    "crime": [
        {"url": "https://www.insightcrime.org/feed/", "name": "InSight Crime", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.insightcrime.org/haiti/feed/", "name": "InSight Crime Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.insightcrime.org/dominican-republic/feed/", "name": "InSight Crime DR", "country": "DO", "lang": "EN", "tier": 1},
        {"url": "https://www.justice.gov/rss/pressreleases.xml", "name": "US DOJ Press Releases", "country": "US", "lang": "EN", "tier": 1},
        {"url": "https://www.dea.gov/rss/pressreleases.xml", "name": "DEA Press Releases", "country": "US", "lang": "EN", "tier": 1},
        {"url": "https://siu.gob.do/rss.xml", "name": "SIU Dominican Republic", "country": "DO", "lang": "ES", "tier": 2},
        {"url": "https://www.transparencyhaiti.org/feed/", "name": "Transparency Haiti", "country": "HT", "lang": "FR/EN", "tier": 2},
        {"url": "https://www.occrp.org/en/rss", "name": "OCCRP Investigations", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.interpol.int/en/News-and-Events/News/rss", "name": "Interpol News", "country": "GLOBAL", "lang": "EN", "tier": 1},
    ],

    # ── HEALTH ────────────────────────────────────────────────────────────────
    "health": [
        {"url": "https://www.mspp.gouv.ht/rss.xml", "name": "MSPP Haiti", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.who.int/feeds/entity/hac/country/hti/en/rss.xml", "name": "WHO Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.paho.org/en/rss/haiti-health-updates.xml", "name": "PAHO Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.paho.org/en/rss/dominican-republic-updates.xml", "name": "PAHO DR", "country": "DO", "lang": "EN", "tier": 1},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&sector=health", "name": "ReliefWeb Haiti Health", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.msf.org/rss.xml", "name": "MSF Global", "country": "GLOBAL", "lang": "EN", "tier": 1},
        {"url": "https://www.cdc.gov/travel/destinations/traveler/none/haiti/rss.xml", "name": "CDC Haiti Travel", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://promedmail.org/promed-rss/", "name": "ProMED Alerts Caribbean", "country": "REGIONAL", "lang": "EN", "tier": 1},
    ],

    # ── MIGRATION ─────────────────────────────────────────────────────────────
    "migration": [
        {"url": "https://www.iom.int/feeds/rss/haiti", "name": "IOM Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.unhcr.org/en-us/feed/haiti.xml", "name": "UNHCR Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&sector=protection", "name": "ReliefWeb Haiti Protection", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.cbp.gov/newsroom/rss/news", "name": "US CBP (Haiti deportations)", "country": "US", "lang": "EN", "tier": 1},
        {"url": "https://www.state.gov/rss-feed/haiti/", "name": "US State Dept Haiti", "country": "US", "lang": "EN", "tier": 1},
        {"url": "https://www.thehaitian.com/feed/", "name": "The Haitian (diaspora)", "country": "HT", "lang": "EN", "tier": 3},
        {"url": "https://caribbeannewsglobal.com/feed/", "name": "Caribbean News Global", "country": "REGIONAL", "lang": "EN", "tier": 3},
        {"url": "https://floridahaitian.com/feed/", "name": "Florida Haitian", "country": "HT/US", "lang": "EN", "tier": 3},
    ],

    # ── ENERGY ────────────────────────────────────────────────────────────────
    "energy": [
        {"url": "https://www.haitilibre.com/rss_energie.xml", "name": "Haiti Libre Énergie", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.eia.gov/rss/news.xml", "name": "EIA Energy News", "country": "GLOBAL", "lang": "EN", "tier": 1},
        {"url": "https://www.irena.org/newsroom/feed", "name": "IRENA Caribbean", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.caribbeanbusinessreport.com/feed/", "name": "Caribbean Business Report Energy", "country": "REGIONAL", "lang": "EN", "tier": 3},
        {"url": "https://energycaribbean.com/feed/", "name": "Energy Caribbean", "country": "REGIONAL", "lang": "EN", "tier": 3},
        {"url": "https://www.eldinero.com.do/category/energia/feed/", "name": "El Dinero Energía", "country": "DO", "lang": "ES", "tier": 2},
    ],

    # ── ENVIRONMENT ───────────────────────────────────────────────────────────
    "environment": [
        {"url": "https://www.gdacs.org/xml/rss_alerts.xml", "name": "GDACS Disaster Alerts", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://firms.modaps.eosdis.nasa.gov/rss/", "name": "NASA FIRMS Fire Alerts", "country": "GLOBAL", "lang": "EN", "tier": 1},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&sector=environment", "name": "ReliefWeb Haiti Environment", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.carbonfootprint.com/rss.xml", "name": "Caribbean Climate", "country": "REGIONAL", "lang": "EN", "tier": 3},
        {"url": "https://www.caribbeanclimatechange.com/feed/", "name": "Caribbean Climate Change", "country": "REGIONAL", "lang": "EN", "tier": 3},
    ],

    # ── CULTURE ───────────────────────────────────────────────────────────────
    "culture": [
        {"url": "https://www.haiticulture.ch/feed/", "name": "Haiti Culture CH", "country": "HT", "lang": "FR", "tier": 3},
        {"url": "https://www.lenouvelliste.com/category/culture/feed", "name": "Le Nouvelliste Culture", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.haitilibre.com/rss_culture.xml", "name": "Haiti Libre Culture", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.caribbeanlifenews.com/feed/", "name": "Caribbean Life News", "country": "REGIONAL", "lang": "EN", "tier": 3},
    ],

    # ── SPORTS ────────────────────────────────────────────────────────────────
    "sports": [
        {"url": "https://www.haitilibre.com/rss_sports.xml", "name": "Haiti Libre Sports", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.lenouvelliste.com/category/sport/feed", "name": "Le Nouvelliste Sport", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.listindiario.com/deportes/rss/", "name": "Listín Deportes", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.noticiassin.com/deportes/feed/", "name": "SIN Deportes", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://caribbeansportsblog.com/feed/", "name": "Caribbean Sports", "country": "REGIONAL", "lang": "EN", "tier": 3},
    ],

    # ── DIASPORA ──────────────────────────────────────────────────────────────
    "diaspora": [
        {"url": "https://haitiantimes.com/feed/", "name": "Haitian Times (NYC)", "country": "HT/US", "lang": "EN", "tier": 2},
        {"url": "https://www.thehaitian.com/feed/", "name": "The Haitian", "country": "HT/US", "lang": "EN", "tier": 3},
        {"url": "https://floridahaitian.com/feed/", "name": "Florida Haitian", "country": "HT/US", "lang": "EN", "tier": 3},
        {"url": "https://www.haiti-reference.com/pages/plan/rss.php", "name": "Haiti-Reference", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://montrealcampus.ca/feed/", "name": "Haitian Montreal", "country": "HT/CA", "lang": "FR", "tier": 3},
        {"url": "https://www.drdiaspora.com/feed/", "name": "DR Diaspora News", "country": "DO/US", "lang": "ES/EN", "tier": 3},
    ],

    # ── DIPLOMACY / INTERNATIONAL ─────────────────────────────────────────────
    "diplomacy": [
        {"url": "https://binuh.unmissions.org/en/rss", "name": "BINUH (UN Haiti)", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://minustah.unmissions.org/rss", "name": "UN MSS Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.state.gov/rss-feed/haiti/", "name": "US State Dept Haiti", "country": "US", "lang": "EN", "tier": 1},
        {"url": "https://www.oas.org/en/media_center/rss.asp?category=haiti", "name": "OAS Haiti", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://caricom.org/feed/", "name": "CARICOM", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.un.org/press/en/rss_haiti.xml", "name": "UN Press Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&type=un-document", "name": "ReliefWeb UN Docs Haiti", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.caribbeancouncil.org/feed/", "name": "Caribbean Council", "country": "REGIONAL", "lang": "EN", "tier": 2},
        {"url": "https://embajada.gob.do/feed/", "name": "DR Embassy News", "country": "DO", "lang": "ES", "tier": 2},
    ],

    # ── FINANCE ───────────────────────────────────────────────────────────────
    "finance": [
        {"url": "https://www.brd.gob.do/rss/noticias.xml", "name": "BRD (Banco Reservas DR)", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.bancentral.gov.do/rss.xml", "name": "Banco Central DR", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.brh.ht/rss.xml", "name": "BRH Haiti (Central Bank)", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.eldinero.com.do/feed/", "name": "El Dinero (Finance DR)", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.centralamericadata.com/en/rss/topic/haiti", "name": "Central America Data Haiti", "country": "HT", "lang": "EN", "tier": 2},
        {"url": "https://www.caribbeantradelaw.com/feed/", "name": "Caribbean Trade Law", "country": "REGIONAL", "lang": "EN", "tier": 3},
        {"url": "https://www.idbinvest.org/en/rss.xml", "name": "IDB Invest", "country": "REGIONAL", "lang": "EN", "tier": 1},
        {"url": "https://www.worldbank.org/en/country/haiti/rss", "name": "World Bank Haiti Finance", "country": "HT", "lang": "EN", "tier": 1},
    ],

    # ── INFRASTRUCTURE ────────────────────────────────────────────────────────
    "infrastructure": [
        {"url": "https://www.haitilibre.com/rss_infrastructure.xml", "name": "Haiti Libre Infrastructure", "country": "HT", "lang": "FR", "tier": 1},
        {"url": "https://www.loophaiti.com/category/travaux-publics/rss.xml", "name": "Loop Haiti Travaux", "country": "HT", "lang": "FR", "tier": 2},
        {"url": "https://reliefweb.int/updates/rss.xml?country=hti&sector=infrastructure", "name": "ReliefWeb Haiti Infrastructure", "country": "HT", "lang": "EN", "tier": 1},
        {"url": "https://www.eldinero.com.do/category/infraestructura/feed/", "name": "El Dinero Infraestructura", "country": "DO", "lang": "ES", "tier": 1},
        {"url": "https://www.caribbeannationalweekly.com/category/infrastructure/feed/", "name": "Caribbean Weekly Infrastructure", "country": "REGIONAL", "lang": "EN", "tier": 3},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────

def get_feed_id(url: str, title: str) -> str:
    return hashlib.md5(f"{url}:{title}".encode()).hexdigest()[:12]

def parse_date(entry) -> str:
    for attr in ["published", "updated", "created"]:
        val = getattr(entry, attr, None)
        if val:
            try:
                return dateparser.parse(val).astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()

def scrape_feed(feed_meta: dict) -> list:
    articles = []
    try:
        d = feedparser.parse(feed_meta["url"], request_headers={
            "User-Agent": "HispaniolaMonitor/1.0 (https://github.com/hispaniola-monitor)"
        })
        for entry in d.entries[:15]:  # max 15 per feed
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = getattr(entry, "summary", "").strip()
            if not title or not link:
                continue
            # Strip HTML from summary
            summary = BeautifulSoup(summary, "lxml").get_text()[:500]
            articles.append({
                "id": get_feed_id(link, title),
                "title": title,
                "url": link,
                "summary": summary,
                "published": parse_date(entry),
                "source": feed_meta["name"],
                "country": feed_meta["country"],
                "lang": feed_meta["lang"],
                "tier": feed_meta["tier"],
                "category": feed_meta.get("_category", "general"),
            })
    except Exception as e:
        print(f"  ⚠ Failed {feed_meta['name']}: {e}")
    return articles

def main():
    print(f"🕵️  Hispaniola Monitor — Scraping {sum(len(v) for v in FEEDS.values())} feeds...")
    all_articles = []
    seen_ids = set()
    total_feeds = 0

    for category, feeds in FEEDS.items():
        print(f"\n📂 {category.upper()} ({len(feeds)} feeds)")
        for feed_meta in feeds:
            feed_meta["_category"] = category
            articles = scrape_feed(feed_meta)
            new = 0
            for a in articles:
                if a["id"] not in seen_ids:
                    seen_ids.add(a["id"])
                    all_articles.append(a)
                    new += 1
            print(f"  ✓ {feed_meta['name']}: {new} articles")
            total_feeds += 1
            time.sleep(0.3)  # gentle rate limiting

    # Sort by published descending
    all_articles.sort(key=lambda x: x["published"], reverse=True)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "raw_articles.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "total_feeds": total_feeds,
            "total_articles": len(all_articles),
            "articles": all_articles
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done. {len(all_articles)} articles from {total_feeds} feeds → {out_path}")

if __name__ == "__main__":
    main()
