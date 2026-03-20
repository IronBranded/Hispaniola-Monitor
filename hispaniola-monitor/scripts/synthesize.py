#!/usr/bin/env python3
"""
Hispaniola Monitor — AI Synthesis
Generates category briefs and an executive summary using Groq (cloud) or Ollama (local).
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "public/data")

SYSTEM_PROMPT = """You are the lead intelligence analyst for Hispaniola Monitor, 
a specialized intelligence platform covering Haiti and the Dominican Republic.
Your analysis is direct, factual, and actionable. You write in English.
Never use corporate or diplomatic hedging. Identify patterns, risks, and significance.
Keep each brief to 3-4 sentences maximum. Lead with the most critical development."""

CATEGORY_PROMPTS = {
    "politics": "Summarize the key political developments in Haiti and the Dominican Republic based on these headlines. Focus on governmental stability, elections, leadership changes, and inter-country tensions.",
    "security": "Analyze the security situation in Haiti and DR based on these headlines. Identify gang activity patterns, territorial changes, and escalation trends. Name specific groups when mentioned.",
    "economy": "Synthesize the economic picture for Haiti and DR. Focus on gourde/peso stability, fuel availability, remittances, and trade.",
    "disaster": "Summarize natural hazard and disaster developments. Haiti sits on the Enriquillo fault. Note earthquake risk, hurricane season status, flood events.",
    "crime": "Analyze criminal network activity in Haiti and DR. Focus on drug trafficking routes, gang leadership changes, and cross-border criminal activity.",
    "health": "Synthesize public health developments. Cholera remains endemic in Haiti. Note outbreak trends, healthcare access, and international medical response.",
    "migration": "Analyze migration patterns between Haiti, DR, and toward the US. Note deportation flows, border closures, and IDP movements within Haiti.",
    "diplomacy": "Summarize international engagement with Haiti and DR. Note UN Security Council discussions, bilateral agreements, sanctions, and multilateral force deployments.",
    "finance": "Brief on financial developments: exchange rates, banking sector news, remittance flows, and major corporate developments in both countries.",
    "infrastructure": "Summarize infrastructure developments: ports, roads, electricity grid, telecommunications.",
}

def call_groq(messages: list, api_key: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def call_ollama(messages: list) -> str:
    import requests
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "llama3.1",
        "messages": messages,
        "stream": False,
        "options": {"num_predict": 300, "temperature": 0.3}
    })
    return response.json()["message"]["content"].strip()

def synthesize_brief(headlines: list, category: str, backend: str, api_key: str = None) -> str:
    if not headlines:
        return "No recent developments in this category."
    
    headline_text = "\n".join([f"- {h['title']} ({h['source']}, {h['published'][:10]})" 
                                for h in headlines[:20]])
    
    prompt = CATEGORY_PROMPTS.get(category, f"Summarize these {category} developments.")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{prompt}\n\nHEADLINES:\n{headline_text}"}
    ]
    
    try:
        if backend == "groq":
            return call_groq(messages, api_key)
        elif backend == "ollama":
            return call_ollama(messages)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    except Exception as e:
        print(f"  ⚠ AI synthesis failed for {category}: {e}")
        return f"Brief unavailable — synthesis error. Latest: {headlines[0]['title'] if headlines else 'No data'}."

def synthesize_executive_summary(briefs: dict, backend: str, api_key: str = None) -> str:
    brief_text = "\n".join([f"[{cat.upper()}] {brief}" for cat, brief in briefs.items() if brief])
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""Write a 5-sentence executive intelligence summary for Hispaniola Monitor.
Identify the most critical developments across Haiti and the Dominican Republic right now.
Highlight any cross-domain convergences (e.g., gang activity + fuel crisis + migration).
Lead with the single most important development.

CATEGORY BRIEFS:
{brief_text}"""}
    ]
    
    try:
        if backend == "groq":
            return call_groq(messages, api_key)
        elif backend == "ollama":
            return call_ollama(messages)
    except Exception as e:
        print(f"  ⚠ Executive summary failed: {e}")
        return "Executive summary unavailable."

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["groq", "ollama"], default="groq")
    args = parser.parse_args()

    api_key = os.environ.get("GROQ_API_KEY") if args.backend == "groq" else None
    if args.backend == "groq" and not api_key:
        print("ERROR: GROQ_API_KEY not set. Use --backend ollama or set the env var.")
        sys.exit(1)

    print(f"🤖 AI Synthesis — backend: {args.backend}")

    # Load raw articles
    raw_path = os.path.join(OUTPUT_DIR, "raw_articles.json")
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)
    
    articles = data["articles"]
    
    # Group by category
    by_category = {}
    for a in articles:
        cat = a.get("category", "general")
        by_category.setdefault(cat, []).append(a)
    
    # Synthesize per-category briefs
    briefs = {}
    for category, headlines in by_category.items():
        print(f"  ✍  Synthesizing {category} ({len(headlines)} articles)...")
        briefs[category] = synthesize_brief(headlines, category, args.backend, api_key)
    
    # Executive summary
    print("  ✍  Generating executive summary...")
    executive = synthesize_executive_summary(briefs, args.backend, api_key)
    
    # Save
    out = {
        "synthesized_at": datetime.now(timezone.utc).isoformat(),
        "backend": args.backend,
        "executive_summary": executive,
        "category_briefs": briefs,
    }
    
    out_path = os.path.join(OUTPUT_DIR, "synthesis.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Synthesis complete → {out_path}")

if __name__ == "__main__":
    main()
