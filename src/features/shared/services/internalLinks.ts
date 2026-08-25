import indexData from '../../../data/restaurants/_index.json';
import { CALCULATORS, type CalculatorMeta } from '../../calculators/shared/registry';

export interface RelatedRestaurantItem {
  slug: string;
  name: string;
  category: string;
  itemCount: number;
  emoji: string;
  url: string;
}

export interface RelatedCalculatorItem {
  slug: string;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
  icon: string;
  url: string;
  accent?: string;
}

export interface CategoryHubItem {
  name: string;
  count: number;
  url: string;
}

const allRestaurants = indexData.restaurants;

/**
 * Dynamically computes related restaurants based on category, peer similarity,
 * and high-value nutritional data, ensuring no restaurant is ever an orphan.
 */
export function getRelatedRestaurants(
  currentSlug: string,
  category?: string,
  limit: number = 6
): RelatedRestaurantItem[] {
  const currentNormalizedSlug = currentSlug.toLowerCase().trim();
  const normalizedCategory = (category || '').toLowerCase().trim();

  // 1. First priority: Peer restaurants in the exact same category
  const sameCategory = allRestaurants.filter(
    (r) =>
      r.slug.toLowerCase() !== currentNormalizedSlug &&
      (r.category || '').toLowerCase().trim() === normalizedCategory
  );

  // Sort same-category restaurants deterministically (or by largest menu)
  const results: RelatedRestaurantItem[] = [];
  const addedSlugs = new Set<string>([currentNormalizedSlug]);

  for (const r of sameCategory) {
    if (results.length >= limit) break;
    results.push({
      slug: r.slug,
      name: r.name,
      category: r.category || 'Restaurant',
      itemCount: r.itemCount || 0,
      emoji: r.emoji || '🍽️',
      url: `/restaurants/${r.slug}/`,
    });
    addedSlugs.add(r.slug.toLowerCase());
  }

  // 2. Second priority: If fewer than limit, pull top popular/high-item chains
  if (results.length < limit) {
    const popularFallbacks = [
      'mcdonalds-calories-calculator',
      'pizza-hut-nutrition-calculator',
      'starbucks-nutrition-calculator',
      'subway-nutrition-calculator',
      'chick-fil-a-nutrition-calculator',
      'chipotle-nutrition-calculator',
      'taco-bell-nutrition-calculator',
      'kfc-nutrition-calculator',
      'olive-garden-nutrition-calculator',
      'dominos-nutrition-calculator',
      'wendys-nutrition-calculator',
      'burger-king-calories-calculator',
    ];

    for (const slug of popularFallbacks) {
      if (results.length >= limit) break;
      if (!addedSlugs.has(slug)) {
        const found = allRestaurants.find((r) => r.slug === slug);
        if (found) {
          results.push({
            slug: found.slug,
            name: found.name,
            category: found.category || 'Restaurant',
            itemCount: found.itemCount || 0,
            emoji: found.emoji || '🍽️',
            url: `/restaurants/${found.slug}/`,
          });
          addedSlugs.add(found.slug.toLowerCase());
        }
      }
    }
  }

  // 3. Third priority: If still fewer, pull from remaining sorted by item count
  if (results.length < limit) {
    const remaining = [...allRestaurants]
      .filter((r) => !addedSlugs.has(r.slug.toLowerCase()))
      .sort((a, b) => (b.itemCount || 0) - (a.itemCount || 0));

    for (const r of remaining) {
      if (results.length >= limit) break;
      results.push({
        slug: r.slug,
        name: r.name,
        category: r.category || 'Restaurant',
        itemCount: r.itemCount || 0,
        emoji: r.emoji || '🍽️',
        url: `/restaurants/${r.slug}/`,
      });
      addedSlugs.add(r.slug.toLowerCase());
    }
  }

  return results;
}

/**
 * Returns companion health & nutrition calculators tailored to the context.
 */
export function getCompanionCalculators(
  contextType: 'restaurant' | 'calculator' | 'food',
  currentCalculatorSlug?: string,
  limit: number = 4
): RelatedCalculatorItem[] {
  const currentSlug = (currentCalculatorSlug || '').toLowerCase().trim();

  let preferredSlugs: string[] = [];

  if (contextType === 'restaurant') {
    // When eating out, users most often need Deficit, Macro, TDEE, and Protein calculators
    preferredSlugs = ['calorie-deficit', 'macro', 'tdee', 'protein', 'bmi'];
  } else if (currentSlug === 'bmi' || currentSlug === 'body-fat' || currentSlug === 'ideal-weight') {
    preferredSlugs = ['body-fat', 'ideal-weight', 'bmi', 'tdee', 'calorie-deficit'];
  } else if (currentSlug === 'bmr' || currentSlug === 'tdee' || currentSlug === 'calorie-deficit') {
    preferredSlugs = ['tdee', 'bmr', 'calorie-deficit', 'macro', 'protein'];
  } else if (currentSlug === 'macro' || currentSlug === 'protein') {
    preferredSlugs = ['macro', 'protein', 'calorie-deficit', 'tdee', 'water-intake'];
  } else {
    preferredSlugs = ['calorie-deficit', 'macro', 'tdee', 'bmi', 'protein', 'water-intake'];
  }

  const results: RelatedCalculatorItem[] = [];
  const seen = new Set<string>();
  if (currentSlug) seen.add(currentSlug);

  for (const slug of preferredSlugs) {
    if (results.length >= limit) break;
    if (!seen.has(slug)) {
      const calc = CALCULATORS.find((c) => c.slug === slug);
      if (calc) {
        results.push({
          slug: calc.slug,
          name: calc.name,
          shortName: calc.shortName,
          tagline: calc.tagline,
          description: calc.description,
          icon: calc.icon,
          url: `/calculators/${calc.slug}/`,
          accent: calc.accent,
        });
        seen.add(slug);
      }
    }
  }

  // Fill up if needed
  if (results.length < limit) {
    for (const calc of CALCULATORS) {
      if (results.length >= limit) break;
      if (!seen.has(calc.slug)) {
        results.push({
          slug: calc.slug,
          name: calc.name,
          shortName: calc.shortName,
          tagline: calc.tagline,
          description: calc.description,
          icon: calc.icon,
          url: `/calculators/${calc.slug}/`,
          accent: calc.accent,
        });
        seen.add(calc.slug);
      }
    }
  }

  return results;
}

/**
 * Returns featured dining category hubs for cross-linking.
 */
export function getCategoryHubs(excludeCategory?: string, limit: number = 8): CategoryHubItem[] {
  const counts = new Map<string, number>();
  for (const r of allRestaurants) {
    const cat = r.category || 'Fast Casual & Dining';
    counts.set(cat, (counts.get(cat) || 0) + 1);
  }

  const normalizedExclude = (excludeCategory || '').toLowerCase().trim();

  return [...counts.entries()]
    .filter(([name]) => name.toLowerCase().trim() !== normalizedExclude)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([name, count]) => ({
      name,
      count,
      url: `/restaurants/#${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
    }));
}

/**
 * Returns featured restaurant links for calculators to bridge fitness tools to real food data.
 */
export function getFeaturedRestaurantsForCalculators(limit: number = 6): RelatedRestaurantItem[] {
  const targetSlugs = [
    'chick-fil-a-nutrition-calculator',
    'chipotle-nutrition-calculator',
    'subway-nutrition-calculator',
    'sweetgreen-nutrition-calculator',
    'cava-nutrition-calculator',
    'panera-bread-nutrition-calculator',
  ];

  const results: RelatedRestaurantItem[] = [];
  for (const slug of targetSlugs) {
    const found = allRestaurants.find((r) => r.slug === slug);
    if (found) {
      results.push({
        slug: found.slug,
        name: found.name,
        category: found.category || 'Healthy & Bowls',
        itemCount: found.itemCount || 0,
        emoji: found.emoji || '🥗',
        url: `/restaurants/${found.slug}/`,
      });
    }
  }

  return results;
}
