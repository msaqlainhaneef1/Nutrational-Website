import type { Restaurant, MenuItem } from '../schemas/restaurant';

const restaurantFiles = import.meta.glob('../../../data/restaurants/*.json', { eager: true });
const restaurants: Restaurant[] = Object.values(restaurantFiles).map((mod: any) => {
  const data = mod.default || mod;
  let name = data.name || data.title || '';
  
  // Strip emojis from the beginning of the title using Extended_Pictographic property escape
  name = name.replace(/^[\s\p{Extended_Pictographic}]+/gu, '').trim();
  
  // Strip common calculator suffixes
  name = name.replace(/\s+(Nutrition|Calories|Calorie)?\s*Calculator$/gi, '').trim();
  
  return {
    ...data,
    name
  };
}).sort((a, b) => a.name.localeCompare(b.name));

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
