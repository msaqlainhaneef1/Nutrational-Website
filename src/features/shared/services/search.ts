export interface PagefindSearchResult {
  url: string;
  excerpt: string;
  meta: {
    title: string;
    [key: string]: any;
  };
}

export async function searchStaticIndex(query: string): Promise<PagefindSearchResult[]> {
  if (typeof window === 'undefined') return [];
  
  try {
    // @ts-ignore
    const pagefind = await import('/pagefind/pagefind.js');
    await pagefind.options({});
    const search = await pagefind.search(query);
    const results = await Promise.all(search.results.slice(0, 10).map((r: any) => r.data()));
    return results;
  } catch (err) {
    console.warn('Pagefind index is not available in development mode.', err);
    return [];
  }
}
