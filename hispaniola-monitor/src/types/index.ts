// ─── Core Intelligence Feed Types ────────────────────────────────────────────

export interface IntelFeedMeta {
  generated_at: string;
  version: string;
  project: string;
  total_articles: number;
  total_feeds_scraped: number;
}

export interface Article {
  id: string;
  title: string;
  url: string;
  summary: string;
  published: string;
  source: string;
  country: string;
  lang: string;
  tier: number;
  category: string;
}

export interface CIISignals {
  gang_security: number;
  political_stability: number;
  economic_distress: number;
  fuel_scarcity: number;
  displacement_idp: number;
  disease_health: number;
  natural_disaster: number;
  border_tension: number;
  diaspora_remittance: number;
  media_freedom: number;
  international_presence: number;
  social_unrest_velocity: number;
}

export interface CIICountry {
  country: string;
  composite_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  trend: 'deteriorating' | 'stable' | 'improving';
  signals: CIISignals;
  signal_article_counts: Partial<CIISignals>;
  computed_at: string;
}

export interface Commodity {
  symbol: string;
  name: string;
  unit: string;
  relevance: string;
  price: number | null;
  prev_close?: number;
  change_pct?: number;
  status: string;
}

export interface Company {
  name: string;
  country: string;
  sector: string;
  ticker: string | null;
  notes: string;
}

export interface ExchangeRates {
  USD_HTG: number | null;
  USD_DOP: number | null;
  source: string;
  timestamp?: string;
}

export interface MarketComposite {
  composite_score: number;
  signals: Array<{ signal: string; value: number; impact: string }>;
  interpretation: string;
}

export interface Criminal {
  rank: number;
  name: string;
  alias: string;
  organization: string;
  role: string;
  status: 'active' | 'arrested' | 'wanted' | 'fugitive' | 'deceased' | 'investigated' | 'prosecuted' | 'emerging';
  threat_level: 'critical' | 'high' | 'medium' | 'low';
  territories: string[];
  coordinates: [number, number];
  country: string;
  sanctions: string[];
  description: string;
  sources: string[];
  last_known_activity?: string;
}

export interface LiveStream {
  name: string;
  country: string;
  type: string;
  url: string;
  embed_id: string | null;
  language: string;
  description: string;
}

export interface GangTerritoryPoint {
  name: string;
  organization: string;
  lat: number;
  lng: number;
  threat_level: string;
  country: string;
  type: string;
}

export interface IntelFeed {
  meta: IntelFeedMeta;
  executive_summary: string;
  category_briefs: Record<string, string>;
  articles: Article[];
  cii: {
    HT: CIICountry;
    DO: CIICountry;
  };
  finance: {
    exchange_rates: ExchangeRates;
    commodities: Commodity[];
    companies: Company[];
    market_composite: MarketComposite;
  };
  criminal_intelligence: {
    haiti: { total_tracked: number; active: number; criminals: Criminal[] };
    dominican_republic: { total_tracked: number; active: number; criminals: Criminal[] };
  };
  live_streams: LiveStream[];
  map_data: {
    gang_territories: GangTerritoryPoint[];
    crisis_points: any[];
    border_crossings: any[];
    key_infrastructure: any[];
  };
}

// ─── UI State Types ───────────────────────────────────────────────────────────

export type MapEngine = 'globe' | 'flat';
export type ActiveTab = 'news' | 'cii' | 'finance' | 'criminals' | 'streams' | 'subscribe';

export interface ActiveLayers {
  gangTerritories: boolean;
  crisisPoints: boolean;
  borderCrossings: boolean;
  infrastructure: boolean;
  earthquakeZones: boolean;
  hurricaneTracks: boolean;
}
