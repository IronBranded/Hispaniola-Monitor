#!/usr/bin/env python3
"""
Hispaniola Monitor — Criminal Intelligence
Maintains curated data on top gang leaders and criminal networks.
This is a static-seed file updated periodically from:
- InSight Crime
- BINUH / UN reports
- JILAP (Justice and Peace)
- Haiti investigative journalism
"""

import json
import os
from datetime import datetime, timezone

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

# ─────────────────────────────────────────────────────────────────────────────
# HAITI — TOP GANG LEADERS & CRIMINAL NETWORKS
# Sources: InSight Crime, BINUH, JILAP, Le Nouvelliste
# ─────────────────────────────────────────────────────────────────────────────
HAITI_CRIMINALS = [
    {
        "rank": 1,
        "name": "Jimmy 'Barbecue' Chérizier",
        "alias": "Barbecue",
        "organization": "Viv Ansanm coalition / G9 an Fanmi e Alye",
        "role": "Federation leader",
        "status": "active",
        "threat_level": "critical",
        "territories": ["Cité Soleil", "Martissant", "Carrefour-Feuilles", "Bas-Ravine"],
        "coordinates": [18.5792, -72.3288],  # Cité Soleil approximate
        "country": "HT",
        "last_known_activity": "2024 Port-au-Prince offensive",
        "sanctions": ["US Treasury OFAC SDN - March 2024", "UN Security Council"],
        "description": "Former police officer turned gang leader. Commands the largest gang coalition in Haiti history (Viv Ansanm), controlling roughly 80% of Port-au-Prince metropolitan area as of 2024.",
        "sources": ["insightcrime.org", "BINUH reports", "US Treasury OFAC"],
    },
    {
        "rank": 2,
        "name": "Izo",
        "alias": "Izo",
        "organization": "5 Segonn (Five Seconds) / Viv Ansanm",
        "role": "Gang leader — Cité Soleil sector",
        "status": "active",
        "threat_level": "critical",
        "territories": ["Cité Soleil southern sector", "Village de Dieu"],
        "coordinates": [18.5680, -72.3378],
        "country": "HT",
        "sanctions": [],
        "description": "Controls southern Cité Soleil and Village de Dieu. Part of the Viv Ansanm coalition. Known for extreme violence and control of key infrastructure.",
        "sources": ["insightcrime.org", "JILAP"],
    },
    {
        "rank": 3,
        "name": "Ti Gabriel",
        "alias": "Ti Gabriel",
        "organization": "Gran Grif",
        "role": "Gang leader — northern Port-au-Prince",
        "status": "active",
        "threat_level": "critical",
        "territories": ["La Plaine", "Lizon", "Croix-des-Bouquets area"],
        "coordinates": [18.5889, -72.2700],
        "country": "HT",
        "sanctions": [],
        "description": "Commands Gran Grif gang controlling areas northeast of Port-au-Prince including strategic routes toward the DR border and the Malpasse crossing.",
        "sources": ["insightcrime.org", "Le Nouvelliste"],
    },
    {
        "rank": 4,
        "name": "Vitelhomme Innocent",
        "alias": "Vitelhomme",
        "organization": "Kraze Baryè",
        "role": "Gang leader — central Port-au-Prince",
        "status": "active",
        "threat_level": "high",
        "territories": ["Bas-Delmas", "Nazon", "Turgeau"],
        "coordinates": [18.5520, -72.3289],
        "country": "HT",
        "sanctions": ["US Treasury OFAC SDN"],
        "description": "Controls central Port-au-Prince neighborhoods. His Kraze Baryè gang joined the Viv Ansanm coalition in 2023, dramatically expanding coalition control.",
        "sources": ["insightcrime.org", "BINUH"],
    },
    {
        "rank": 5,
        "name": "Chen Mechan leadership",
        "alias": "Chen Mechan",
        "organization": "Chen Mechan (Nasty Dog)",
        "role": "Gang — Delmas 6 axis",
        "status": "active",
        "threat_level": "high",
        "territories": ["Delmas 6", "Route Nationale 1 corridor"],
        "coordinates": [18.5620, -72.3200],
        "country": "HT",
        "sanctions": [],
        "description": "Controls key northern entry to Port-au-Prince along Route Nationale 1, taxing commercial traffic and controlling movement to Cap-Haïtien road.",
        "sources": ["insightcrime.org", "JILAP", "Ayibopost"],
    },
    {
        "rank": 6,
        "name": "Micanor Altès",
        "alias": "Micanor",
        "organization": "400 Mawozo",
        "role": "Key figure — 400 Mawozo",
        "status": "arrested",
        "threat_level": "high",
        "territories": ["Croix-des-Bouquets", "Thomazeau"],
        "coordinates": [18.5780, -72.1970],
        "country": "HT",
        "sanctions": ["US Treasury OFAC SDN"],
        "description": "400 Mawozo masterminded multiple mass kidnappings including 17 American and Canadian missionaries in 2021. Leadership arrested but organization remains active.",
        "sources": ["US DOJ", "insightcrime.org"],
    },
    {
        "rank": 7,
        "name": "Luckson Elan",
        "alias": "Krisla",
        "organization": "Chandèl gang",
        "role": "Gang leader — Artibonite Valley",
        "status": "active",
        "threat_level": "high",
        "territories": ["Liancourt", "Saint-Marc corridor", "Artibonite Valley"],
        "coordinates": [19.1500, -72.5700],
        "country": "HT",
        "sanctions": ["US Treasury OFAC SDN"],
        "description": "Controls the Artibonite Valley, Haiti's rice bowl. Attacks on farmers have contributed to food insecurity across the country.",
        "sources": ["insightcrime.org", "Reuters"],
    },
    {
        "rank": 8,
        "name": "Renel Destina",
        "alias": "Ti Lapli",
        "organization": "Fantom 509",
        "role": "Police-linked gang leader",
        "status": "wanted",
        "threat_level": "high",
        "territories": ["Delmas 95", "Lizon area"],
        "coordinates": [18.5810, -72.3100],
        "country": "HT",
        "sanctions": [],
        "description": "Former police officer linked to Fantom 509, a gang with suspected ties to political networks. Wanted for multiple murders and kidnappings.",
        "sources": ["JILAP", "AlterPresse"],
    },
    {
        "rank": 9,
        "name": "Bélizaire Dauphin",
        "alias": "Kidor",
        "organization": "Base Pilate",
        "role": "Gang leader — Artibonite",
        "status": "active",
        "threat_level": "medium",
        "territories": ["Saint-Marc", "Petite-Rivière de l'Artibonite"],
        "coordinates": [19.1067, -72.6900],
        "country": "HT",
        "sanctions": [],
        "description": "Controls Base Pilate in Artibonite. Competes with Chandèl gang for territorial control of the grain corridor.",
        "sources": ["insightcrime.org", "ReliefWeb"],
    },
    {
        "rank": 10,
        "name": "Unknown — Lamès Kabicha leadership",
        "alias": "Lamès Kabicha",
        "organization": "Lamès Kabicha",
        "role": "Gang — Grand'Anse Department",
        "status": "active",
        "threat_level": "medium",
        "territories": ["Jérémie", "Grand'Anse"],
        "coordinates": [18.6431, -74.1165],
        "country": "HT",
        "sanctions": [],
        "description": "Controls large portions of the Grand'Anse department, the most isolated part of Haiti. Has created a humanitarian corridor blockade cutting off aid.",
        "sources": ["insightcrime.org", "OCHA"],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# DOMINICAN REPUBLIC — TOP CRIMINAL NETWORKS
# ─────────────────────────────────────────────────────────────────────────────
DR_CRIMINALS = [
    {
        "rank": 1,
        "name": "Los Trinitarios leadership",
        "alias": "Los Trinitarios",
        "organization": "Los Trinitarios",
        "role": "National gang network",
        "status": "active",
        "threat_level": "critical",
        "territories": ["Santo Domingo Norte", "Los Alcarrizos", "Pedro Brand", "NYC diaspora wing"],
        "coordinates": [18.5601, -69.9440],
        "country": "DO",
        "sanctions": ["US Treasury OFAC SDN (NYC wing)"],
        "description": "Largest and most dangerous gang in the DR. Founded in New York prisons, now controls vast swaths of Santo Domingo periphery. Has transnational links to NYC drug distribution. Known for extreme loyalty oath and retaliatory violence.",
        "sources": ["insightcrime.org", "US DOJ", "Diario Libre"],
    },
    {
        "rank": 2,
        "name": "Los Yafé leadership",
        "alias": "Los Yafé",
        "organization": "Los Yafé",
        "role": "Drug trafficking organization",
        "status": "active",
        "threat_level": "high",
        "territories": ["Santo Domingo Este", "Boca Chica corridor"],
        "coordinates": [18.4861, -69.8731],
        "country": "DO",
        "sanctions": [],
        "description": "Major cocaine transit network operating through Boca Chica and DR eastern ports. Linked to Colombian cartel supply chains.",
        "sources": ["insightcrime.org", "DNCD DR"],
    },
    {
        "rank": 3,
        "name": "Félix Bautista-linked networks",
        "alias": "La Red",
        "organization": "Political corruption network",
        "role": "Corruption / money laundering",
        "status": "investigated",
        "threat_level": "high",
        "territories": ["Santo Domingo", "Construction sector"],
        "coordinates": [18.4861, -69.9312],
        "country": "DO",
        "sanctions": ["US Treasury OFAC SDN (money laundering)"],
        "description": "Former DR senator linked to money laundering network using construction contracts. Sanctioned by the US for allegedly facilitating corruption during earthquake reconstruction contracts with Haiti.",
        "sources": ["US Treasury", "OCCRP", "insightcrime.org"],
    },
    {
        "rank": 4,
        "name": "Haitian-DR border trafficking networks",
        "alias": "Border Networks",
        "organization": "Multiple cross-border syndicates",
        "role": "Human smuggling / drug transit",
        "status": "active",
        "threat_level": "high",
        "territories": ["Dajabón", "Jimaní", "Pedernales border"],
        "coordinates": [19.5558, -71.7054],
        "country": "DO",
        "sanctions": [],
        "description": "Loosely affiliated networks exploiting the 360km Haiti-DR border. Traffic includes cocaine transiting from Haiti (Caribbean cocaine corridor), Haitian migrants, and contraband goods. Have connections to Haitian gang leadership for border corridor access.",
        "sources": ["insightcrime.org", "InSight Crime DR", "DEA"],
    },
    {
        "rank": 5,
        "name": "Los Peluches leadership",
        "alias": "Los Peluches",
        "organization": "Los Peluches",
        "role": "Urban gang — Santiago",
        "status": "active",
        "threat_level": "medium",
        "territories": ["Santiago de los Caballeros", "La Joya area"],
        "coordinates": [19.4517, -70.6970],
        "country": "DO",
        "sanctions": [],
        "description": "Dominant gang in Santiago, DR's second city. Primarily involved in extortion, territorial control, and drug retail. Has clashed with Los Trinitarios for northern DR influence.",
        "sources": ["insightcrime.org", "Listín Diario"],
    },
    {
        "rank": 6,
        "name": "Operación Coral networks (remnants)",
        "alias": "Coral Networks",
        "organization": "Military-linked corruption",
        "role": "Drug trafficking — military corruption",
        "status": "prosecuted",
        "threat_level": "medium",
        "territories": ["Santo Domingo", "Military bases"],
        "coordinates": [18.4861, -69.9312],
        "country": "DO",
        "sanctions": [],
        "description": "Operación Coral (2017) exposed a network involving 14 active-duty military officers trafficking cocaine. Key figures convicted but successor networks suspected to operate.",
        "sources": ["insightcrime.org", "El Caribe DR"],
    },
    {
        "rank": 7,
        "name": "Caribbean cocaine transit cell (unnamed)",
        "alias": "Caribbean Corridor",
        "organization": "Colombian cartel affiliates",
        "role": "Cocaine transit — Haiti/DR axis",
        "status": "active",
        "threat_level": "high",
        "territories": ["Caribbean coastal routes", "DR northern coast", "Cap-Haïtien HT"],
        "coordinates": [19.7575, -72.2083],
        "country": "HT/DO",
        "sanctions": [],
        "description": "Hispaniola has re-emerged as a major Caribbean cocaine transit corridor. Bolivian/Colombian cocaine moves through Haiti into DR, then north via maritime routes to Puerto Rico and the US mainland. Gang control of Haitian ports (particularly Cap-Haïtien) is key.",
        "sources": ["DEA", "UNODC Caribbean report", "insightcrime.org"],
    },
    {
        "rank": 8,
        "name": "Ranfis Domínguez leadership (Inoa network)",
        "alias": "Inoa",
        "organization": "Inoa family network",
        "role": "Drug trafficker",
        "status": "fugitive",
        "threat_level": "medium",
        "territories": ["Santo Domingo", "US east coast"],
        "coordinates": [18.4861, -69.9312],
        "country": "DO",
        "sanctions": ["US Treasury OFAC SDN"],
        "description": "Dominican trafficking network with US connections. Indicted in US federal court for cocaine distribution. Associates remain active.",
        "sources": ["US DOJ", "DEA", "insightcrime.org"],
    },
    {
        "rank": 9,
        "name": "Peravia port trafficking network",
        "alias": "Peravia Network",
        "organization": "Bani-area traffickers",
        "role": "Port corruption / drug transit",
        "status": "active",
        "threat_level": "medium",
        "territories": ["Baní", "Peravia province coast"],
        "coordinates": [18.2796, -70.3336],
        "country": "DO",
        "sanctions": [],
        "description": "Peravia's southern coast is a known go-fast boat corridor for cocaine coming from South America or the ABC islands. Local corruption of port and customs officials documented.",
        "sources": ["insightcrime.org", "UNODC"],
    },
    {
        "rank": 10,
        "name": "Mara Salvatrucha (MS-13) — Caribbean cell",
        "alias": "MS-13 Caribbean",
        "organization": "MS-13",
        "role": "Transnational gang presence",
        "status": "emerging",
        "threat_level": "medium",
        "territories": ["Santo Domingo periphery (emerging)"],
        "coordinates": [18.4861, -69.9440],
        "country": "DO",
        "sanctions": ["US Treasury OFAC SDN (global)"],
        "description": "MS-13 has been detected attempting to establish presence in the DR, recruiting from the Dominican and Haitian migrant population. Currently assessed as low operational capacity in DR but monitored by DNCD and US DEA.",
        "sources": ["insightcrime.org", "DEA", "Hoy DR"],
    },
]

def main():
    print("🦹 Updating criminal intelligence index...")
    
    out = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "haiti": {
            "total_tracked": len(HAITI_CRIMINALS),
            "active": len([c for c in HAITI_CRIMINALS if c["status"] == "active"]),
            "criminals": HAITI_CRIMINALS,
        },
        "dominican_republic": {
            "total_tracked": len(DR_CRIMINALS),
            "active": len([c for c in DR_CRIMINALS if c["status"] == "active"]),
            "criminals": DR_CRIMINALS,
        }
    }
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "criminals.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Criminal intelligence → {out_path}")
    print(f"  🇭🇹 Haiti: {len(HAITI_CRIMINALS)} tracked ({len([c for c in HAITI_CRIMINALS if c['status']=='active'])} active)")
    print(f"  🇩🇴 DR:    {len(DR_CRIMINALS)} tracked ({len([c for c in DR_CRIMINALS if c['status']=='active'])} active)")

if __name__ == "__main__":
    main()
