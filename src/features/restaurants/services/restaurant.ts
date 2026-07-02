import type { Restaurant, MenuItem } from '../schemas/restaurant';

const restaurantFiles = import.meta.glob('../../../data/restaurants/*.json', { eager: true });
const restaurants: Restaurant[] = Object.values(restaurantFiles).map((mod: any) => mod.default || mod);

export function getAllRestaurants(): Restaurant[] {
  return restaurants;
}

export function getRestaurantBySlug(slug: string): Restaurant | undefined {
  return restaurants.find((res) => res.slug === slug);
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
