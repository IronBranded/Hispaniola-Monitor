import { useState, useEffect, useCallback } from 'react';
import type { IntelFeed } from '../types';

// In dev, load from local file. In production, load from GitHub raw URL.
const FEED_URL = import.meta.env.DEV
  ? '/data/intelligence_feed.json'
  : `${import.meta.env.BASE_URL}data/intelligence_feed.json`;

// Refresh every 30 minutes
const REFRESH_INTERVAL = 30 * 60 * 1000;

export function useIntelFeed() {
  const [feed, setFeed] = useState<IntelFeed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const loadFeed = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch(`${FEED_URL}?t=${Date.now()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: IntelFeed = await res.json();
      setFeed(data);
      setLastRefresh(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load feed');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFeed();
    const interval = setInterval(loadFeed, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [loadFeed]);

  return { feed, loading, error, lastRefresh, refresh: loadFeed };
}
