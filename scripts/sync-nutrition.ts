import fs from 'node:fs';
import path from 'node:path';

/**
 * Optional build-time sync script.
 * Fetches a small set of branded products from Open Food Facts and writes
 * normalized JSON files to src/data/foods/.
 *
 * Usage: node --experimental-strip-types scripts/sync-nutrition.ts
 * (or via tsx: npx tsx scripts/sync-nutrition.ts)
 *
 * This is optional. The repo already ships with hand-curated food data.
 */

import { FoodSchema } from '../src/features/nutrition/schemas/food';

const BARCODES = [
  { barcode: '3017620422003', slug: 'nutella' },
  { barcode: '7622210449283', slug: 'oreo-cookies' },
];

async function syncFoodItem(barcode: string, fileSlug: string) {
  const url = `https://world.openfoodfacts.org/api/v2/product/${barcode}.json`;
  console.log(`[sync] Fetching ${url}`);

  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'NutriFlow - Web App - Version 1.0' },
    });

    if (!res.ok) throw new Error(`OFF API returned status: ${res.status}`);

    const json = (await res.json()) as any;
    if (!json.product) throw new Error(`Product not found for barcode: ${barcode}`);

    const prod = json.product;
    const nutrients = prod.nutriments || {};

    const rawData = {
      name: prod.product_name || 'Generic Food',
      slug: fileSlug,
      description: prod.generic_name || `Statically imported nutrition profile for ${prod.product_name || 'this product'}.`,
      category: prod.categories_tags?.[0]?.replace('en:', '').replace(/-/g, ' ') || 'Packaged Foods',
      servingSize: '100g',
      calories: Math.round(nutrients['energy-kcal_100g'] || 0),
      macros: {
        protein: { value: nutrients.proteins_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.proteins_100g || 0) * 2) },
        fat: { value: nutrients.fat_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.fat_100g || 0) * 1.5) },
        carbs: { value: nutrients.carbohydrates_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.carbohydrates_100g || 0) * 0.3) },
        fiber: { value: nutrients.fiber_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.fiber_100g || 0) * 4) },
        sugar: { value: nutrients.sugars_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.sugars_100g || 0) * 2) },
      },
      micros: {
        sodium: { value: Math.round((nutrients.sodium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.sodium_100g || 0) * 1000 * 0.04) },
        potassium: { value: Math.round((nutrients.potassium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.potassium_100g || 0) * 1000 * 0.02) },
        calcium: { value: Math.round((nutrients.calcium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.calcium_100g || 0) * 1000 * 0.1) },
      },
      faqs: [
        {
          q: `Is ${prod.product_name} high in sugar?`,
          a: `A 100g serving contains ${nutrients.sugars_100g || 0}g of sugar. Check the percent daily value to see how this fits into a 2,000 calorie reference diet.`,
        },
      ],
    };

    const result = FoodSchema.safeParse(rawData);
    if (!result.success) {
      console.error(`[sync] Validation failed for ${rawData.name}:`, result.error.format());
      return;
    }

    const outPath = path.resolve(`src/data/foods/${fileSlug}.json`);
    fs.writeFileSync(outPath, JSON.stringify(result.data, null, 2), 'utf-8');
    console.log(`[sync] Saved to ${outPath}`);
  } catch (err: any) {
    console.warn(`[sync] Skipped ${barcode}: ${err.message}`);
  }
}

async function runSync() {
  console.log('[sync] Starting Open Food Facts sync...');
  for (const item of BARCODES) {
    await syncFoodItem(item.barcode, item.slug);
  }
  console.log('[sync] Done.');
}

runSync();
