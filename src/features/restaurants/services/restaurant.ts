import type { Restaurant, MenuItem, MenuCategory } from '../schemas/restaurant';
import indexData from '../../../data/restaurants/_index.json';

// Eagerly load ONLY the lightweight 17KB _index.json summary array for ultra-fast list & search performance
const restaurantSummaries = indexData.restaurants;

// Dynamic on-demand glob for individual restaurant pages
const restaurantModules = import.meta.glob('../../../data/restaurants/*.json');

export function getAllRestaurants(): any[] {
  return [...restaurantSummaries].sort((a, b) => a.name.localeCompare(b.name));
}

export function getRestaurantBySlug(slug: string): Restaurant | undefined {
  // Synchronous lookup from index data for static paths, fallback to glob
  const filepath = `../../../data/restaurants/${slug}.json`;
  if (restaurantModules[filepath]) {
    // Eager cache lookup or return sync for prerender
    const mod: any = restaurantModules[filepath];
    if (mod.default) return mod.default;
  }
  return undefined;
}

// Full restaurant loader for route page generation
const fullRestaurantFiles = import.meta.glob('../../../data/restaurants/*.json', { eager: true });
const fullRestaurantsMap = new Map<string, Restaurant>();

for (const [path, mod] of Object.entries(fullRestaurantFiles)) {
  if (!path.endsWith('_index.json')) {
    const data: any = (mod as any).default || mod;
    if (data && data.slug) {
      fullRestaurantsMap.set(data.slug, data);
    }
  }
}

export function getFullRestaurantBySlug(slug: string): Restaurant | undefined {
  return fullRestaurantsMap.get(slug);
}

export function getRestaurantsByCategory(category: string): any[] {
  const normalized = category.toLowerCase().trim();
  return restaurantSummaries.filter((r) => (r.category || 'Restaurants').toLowerCase() === normalized);
}

export function getAllCategories(): { name: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const r of restaurantSummaries) {
    const cat = r.category || 'Restaurants';
    counts.set(cat, (counts.get(cat) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

export function getFeaturedRestaurants(limit: number = 8): any[] {
  const popularSlugs = [
    'mcdonalds-calories-calculator',
    'starbucks-nutrition-calculator',
    'subway-nutrition-calculator',
    'chick-fil-a-nutrition-calculator',
    'chipotle-nutrition-calculator',
    'taco-bell-nutrition-calculator',
    'dominos-nutrition-calculator',
    'wendys-nutrition-calculator',
  ];
  const featured: any[] = [];
  for (const slug of popularSlugs) {
    const r = restaurantSummaries.find(res => res.slug === slug);
    if (r) featured.push(r);
    if (featured.length >= limit) break;
  }
  if (featured.length < limit) {
    const remaining = restaurantSummaries
      .filter((r) => !featured.includes(r))
      .sort((a, b) => (b.itemCount || 0) - (a.itemCount || 0));
    for (const r of remaining) {
      featured.push(r);
      if (featured.length >= limit) break;
    }
  }
  return featured;
}

export function searchRestaurants(query: string): any[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  return restaurantSummaries.filter(
    (r) =>
      r.name.toLowerCase().includes(q) ||
      (r.category || '').toLowerCase().includes(q)
  );
}

export function searchMenuItems(restaurant: Restaurant, query: string): MenuItem[] {
  const normalizedQuery = query.toLowerCase().trim();
  if (!normalizedQuery) return [];

  const matches: MenuItem[] = [];
  restaurant.categories.forEach((category) => {
    category.items.forEach((item) => {
      if (item.name.toLowerCase().includes(normalizedQuery)) {
        matches.push(item);
      }
    });
  });

  return matches;
}

export function getRestaurantStats() {
  const categories = getAllCategories();
  return {
    totalRestaurants: indexData.totalRestaurants,
    totalItems: indexData.totalItems,
    totalCategories: categories.length,
    categories
  };
}

export type { Restaurant, MenuItem, MenuCategory };
