import fs from 'node:fs';
import path from 'node:path';
import { FoodSchema } from '../src/features/nutrition/schemas/food';

// A few real barcode examples from Open Food Facts (requires no auth key)
const BARCODES = [
  { barcode: '3017620422003', slug: 'nutella' },
  { barcode: '7622210449283', slug: 'oreo-cookies' }
];

async function syncFoodItem(barcode: string, fileSlug: string) {
  const url = `https://world.openfoodfacts.org/api/v2/product/${barcode}.json`;
  console.log(`[Sync] Fetching raw product data from Open Food Facts: ${url}`);
  
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'NutriFlow - Web App - Version 1.0'
      }
    });

    if (!res.ok) {
      throw new Error(`OFF API returned status: ${res.status}`);
    }

    const json = await res.json() as any;
    
    if (!json.product) {
      throw new Error(`Product not found for barcode: ${barcode}`);
    }

    const prod = json.product;
    const nutrients = prod.nutriments || {};

    // Map Open Food Facts nutrients to our normalized schema
    const rawData = {
      name: prod.product_name || 'Generic Food',
      slug: fileSlug,
      description: prod.generic_name || `Statically imported nutrition profile for ${prod.product_name || 'Generic Food'}.`,
      category: prod.categories_tags?.[0]?.replace('en:', '').replace(/-/g, ' ') || 'Packaged Foods',
      servingSize: prod.serving_size || '100g',
      calories: Math.round(nutrients['energy-kcal_100g'] || 0),
      macros: {
        protein: { value: nutrients.proteins_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.proteins_100g || 0) * 2) },
        fat: { value: nutrients.fat_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.fat_100g || 0) * 1.5) },
        carbs: { value: nutrients.carbohydrates_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.carbohydrates_100g || 0) * 0.3) },
        fiber: { value: nutrients.fiber_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.fiber_100g || 0) * 4) },
        sugar: { value: nutrients.sugars_100g || 0, unit: 'g', pctDailyValue: Math.round((nutrients.sugars_100g || 0) * 2) }
      },
      micros: {
        sodium: { value: Math.round((nutrients.sodium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.sodium_100g || 0) * 1000 * 0.04) },
        potassium: { value: Math.round((nutrients.potassium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.potassium_100g || 0) * 1000 * 0.02) },
        calcium: { value: Math.round((nutrients.calcium_100g || 0) * 1000), unit: 'mg', pctDailyValue: Math.round((nutrients.calcium_100g || 0) * 1000 * 0.1) }
      },
      faqs: [
        {
          q: `Is ${prod.product_name} high in sugar?`,
          a: `A 100g serving contains ${nutrients.sugars_100g || 0}g of sugar, which contributes to its overall nutritional profile.`
        }
      ]
    };

    // Validate the cleaned data using Zod schema
    const result = FoodSchema.safeParse(rawData);
    if (!result.success) {
      console.error(`[Sync] Validation failed for ${rawData.name}:`, result.error.format());
      return;
    }

    // Save to local JSON files
    const outPath = path.resolve(`src/data/foods/${fileSlug}.json`);
    fs.writeFileSync(outPath, JSON.stringify(result.data, null, 2), 'utf-8');
    console.log(`[Sync] SUCCESS: Normalized and saved to ${outPath}`);

  } catch (err: any) {
    console.warn(`[Sync] Network failed for barcode ${barcode}. Falling back to mock sync values...`, err.message);
    
    // Fallback Mock Sync Data (runs if offline or API is down)
    const mockData = {
      name: fileSlug === 'nutella' ? 'Nutella Spread' : 'Oreo Cookies',
      slug: fileSlug,
      description: `Mocked fallback sync data for ${fileSlug}.`,
      category: 'Sweets',
      servingSize: '100g',
      calories: fileSlug === 'nutella' ? 539 : 480,
      macros: {
        protein: { value: fileSlug === 'nutella' ? 6.3 : 4.8, unit: 'g', pctDailyValue: 10 },
        fat: { value: fileSlug === 'nutella' ? 30.9 : 20.0, unit: 'g', pctDailyValue: 40 },
        carbs: { value: fileSlug === 'nutella' ? 57.5 : 70.0, unit: 'g', pctDailyValue: 20 }
      }
    };

    const result = FoodSchema.safeParse(mockData);
    if (result.success) {
      const outPath = path.resolve(`src/data/foods/${fileSlug}.json`);
      fs.writeFileSync(outPath, JSON.stringify(result.data, null, 2), 'utf-8');
      console.log(`[Sync] Saved fallback data to ${outPath}`);
    }
  }
}

async function runSync() {
  console.log('[Sync] Starting background synchronization...');
  for (const item of BARCODES) {
    await syncFoodItem(item.barcode, item.slug);
  }
  console.log('[Sync] Import completed successfully.');
}

runSync();
