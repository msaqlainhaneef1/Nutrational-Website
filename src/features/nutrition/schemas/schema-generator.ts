import type { Food } from './food';

export function createFoodSchema(food: Food, siteUrl: string) {
  const cleanSite = siteUrl.replace(/\/$/, '');
  const canonicalUrl = `${cleanSite}/foods/${food.slug}/`;

  return [
    {
      "@type": "ItemPage",
      "@id": `${canonicalUrl}#itempage`,
      "url": canonicalUrl,
      "name": `${food.name} Nutrition Facts & Macros`,
      "description": food.description || `Complete nutrition profile and macronutrient breakdown for ${food.name} per ${food.servingSize}.`,
      "breadcrumb": {
        "@type": "BreadcrumbList",
        "@id": `${canonicalUrl}#breadcrumb`,
        "itemListElement": [
          {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": `${cleanSite}/`
          },
          {
            "@type": "ListItem",
            "position": 2,
            "name": "Foods",
            "item": `${cleanSite}/foods/`
          },
          {
            "@type": "ListItem",
            "position": 3,
            "name": food.name,
            "item": canonicalUrl
          }
        ]
      },
      "mainEntity": {
        "@type": "NutritionInformation",
        "calories": `${food.calories} kcal`,
        "servingSize": food.servingSize,
        "proteinContent": `${food.macros.protein.value} g`,
        "fatContent": `${food.macros.fat.value} g`,
        "carbohydrateContent": `${food.macros.carbs.value} g`,
        ...(food.macros.fiber ? { "fiberContent": `${food.macros.fiber.value} g` } : {}),
        ...(food.macros.sugar ? { "sugarContent": `${food.macros.sugar.value} g` } : {})
      }
    }
  ];
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
