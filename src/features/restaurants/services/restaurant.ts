import type { Restaurant, MenuItem, MenuCategory } from '../schemas/restaurant';

const restaurantFiles = import.meta.glob('../../../data/restaurants/*.json', { eager: true });
const restaurants: Restaurant[] = Object.entries(restaurantFiles)
  .filter(([path]) => !path.endsWith('_index.json'))
  .map(([, mod]: any) => mod.default || mod);

export function getAllRestaurants(): Restaurant[] {
  return [...restaurants].sort((a, b) => a.name.localeCompare(b.name));
}

export function getRestaurantBySlug(slug: string): Restaurant | undefined {
  return restaurants.find((res) => res.slug === slug);
}

export function getRestaurantsByCategory(category: string): Restaurant[] {
  const normalized = category.toLowerCase().trim();
  return restaurants.filter((r) => (r.category || 'Restaurants').toLowerCase() === normalized);
}

export function getAllCategories(): { name: string; count: number }[] {
  const counts = new Map<string, number>();
  for (const r of restaurants) {
    const cat = r.category || 'Restaurants';
    counts.set(cat, (counts.get(cat) || 0) + 1);
  }
  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
}

export function getFeaturedRestaurants(limit: number = 8): Restaurant[] {
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
  const featured: Restaurant[] = [];
  for (const slug of popularSlugs) {
    const r = getRestaurantBySlug(slug);
    if (r) featured.push(r);
    if (featured.length >= limit) break;
  }
  // Pad with highest-item-count restaurants if needed
  if (featured.length < limit) {
    const remaining = restaurants
      .filter((r) => !featured.includes(r))
      .sort((a, b) => (b.itemCount || 0) - (a.itemCount || 0));
    for (const r of remaining) {
      featured.push(r);
      if (featured.length >= limit) break;
    }
  }
  return featured;
}

export function searchRestaurants(query: string): Restaurant[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];
  return restaurants.filter(
    (r) =>
      r.name.toLowerCase().includes(q) ||
      (r.description || '').toLowerCase().includes(q) ||
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
  const totalItems = restaurants.reduce((sum, r) => sum + (r.itemCount || r.categories.reduce((s, c) => s + c.items.length, 0)), 0);
  const totalRestaurants = restaurants.length;
  const categories = getAllCategories();
  return { totalRestaurants, totalItems, totalCategories: categories.length, categories };
}

export type { Restaurant, MenuItem, MenuCategory };
