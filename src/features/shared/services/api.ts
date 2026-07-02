import fs from 'node:fs';
import path from 'node:path';

const CACHE_DIR = path.resolve('.cache/api-cache');

interface CacheEntry<T> {
  expiresAt: number;
  data: T;
}

const isNode = typeof process !== 'undefined' && process.versions && process.versions.node;

function ensureCacheDir() {
  if (isNode && !fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

export async function fetchWithCache<T>(
  url: string,
  cacheKey: string,
  ttlMs: number = 24 * 60 * 60 * 1000,
  headers: Record<string, string> = {}
): Promise<T> {
  const sanitizedKey = cacheKey.replace(/[^a-z0-9_-]/gi, '_');

  if (isNode) {
    ensureCacheDir();
    const cacheFilePath = path.join(CACHE_DIR, `${sanitizedKey}.json`);

    if (fs.existsSync(cacheFilePath)) {
      try {
        const fileContent = fs.readFileSync(cacheFilePath, 'utf-8');
        const entry: CacheEntry<T> = JSON.parse(fileContent);

        if (Date.now() < entry.expiresAt) {
          console.log(`[API Cache] HIT (File) for key: ${cacheKey}`);
          return entry.data;
        }
      } catch (err) {
        console.warn(`[API Cache] Error reading file cache for key: ${cacheKey}`, err);
      }
    }
  } else if (typeof window !== 'undefined' && window.localStorage) {
    try {
      const stored = localStorage.getItem(`api_cache_${sanitizedKey}`);
      if (stored) {
        const entry: CacheEntry<T> = JSON.parse(stored);
        if (Date.now() < entry.expiresAt) {
          console.log(`[API Cache] HIT (LocalStorage) for key: ${cacheKey}`);
          return entry.data;
        }
      }
    } catch (err) {
      console.warn(`[API Cache] Error reading localstorage cache`, err);
    }
  }

  console.log(`[API Cache] MISS for key: ${cacheKey}. Fetching: ${url}`);
  const response = await fetch(url, { headers });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch from API: ${response.statusText} (${response.status})`);
  }

  const data = (await response.json()) as T;
  const expiresAt = Date.now() + ttlMs;
  const cacheEntry: CacheEntry<T> = { expiresAt, data };

  if (isNode) {
    try {
      const cacheFilePath = path.join(CACHE_DIR, `${sanitizedKey}.json`);
      fs.writeFileSync(cacheFilePath, JSON.stringify(cacheEntry, null, 2), 'utf-8');
    } catch (err) {
      console.error(`[API Cache] Failed to write file cache for key: ${cacheKey}`, err);
    }
  } else if (typeof window !== 'undefined' && window.localStorage) {
    try {
      localStorage.setItem(`api_cache_${sanitizedKey}`, JSON.stringify(cacheEntry));
    } catch (err) {
      console.error(`[API Cache] Failed to write localstorage cache`, err);
    }
  }

  return data;
}
