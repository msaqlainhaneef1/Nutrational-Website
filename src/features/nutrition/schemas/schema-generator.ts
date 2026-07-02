import type { Food } from './food';

export function createFoodSchema(food: Food, siteUrl: string) {
  return {
    "@context": "https://schema.org",
    "@type": "MenuItem",
    "name": food.name,
    "description": food.description || `Nutrition facts for ${food.name}`,
    "nutrition": {
      "@type": "NutritionInformation",
      "calories": `${food.calories} calories`,
      "servingSize": food.servingSize,
      "proteinContent": `${food.macros.protein.value} g`,
      "fatContent": `${food.macros.fat.value} g`,
      "carbohydrateContent": `${food.macros.carbs.value} g`,
      ...(food.macros.fiber ? { "fiberContent": `${food.macros.fiber.value} g` } : {}),
      ...(food.macros.sugar ? { "sugarContent": `${food.macros.sugar.value} g` } : {})
    }
  };
}

export function createArticleSchema(
  title: string,
  description: string,
  url: string,
  pubDate: string,
  author: string
) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": title,
    "description": description,
    "url": url,
    "datePublished": pubDate,
    "author": {
      "@type": "Person",
      "name": author
    }
  };
}
