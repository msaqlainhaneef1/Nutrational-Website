import type { Food } from '../schemas/food';

const foodFiles = import.meta.glob('../../../data/foods/*.json', { eager: true });
const foods: Food[] = Object.values(foodFiles).map((mod: any) => mod.default || mod);

export function getAllFoods(): Food[] {
  return foods;
}

export function getFoodBySlug(slug: string): Food | undefined {
  return foods.find((food) => food.slug === slug);
}

export function getFoodsByCategory(category: string): Food[] {
  return foods.filter((food) => food.category.toLowerCase() === category.toLowerCase());
}

export function getAllCategories(): string[] {
  const categories = foods.map((food) => food.category);
  return [...new Set(categories)];
}

export function scaleNutrients(food: Food, targetWeightG: number): Food {
  const originalWeight = parseFloat(food.servingSize) || 100;
  const factor = targetWeightG / originalWeight;

  const scaleNutrient = (nutrient?: { value: number; unit: string; pctDailyValue?: number }) => {
    if (!nutrient) return undefined;
    return {
      value: Math.round(nutrient.value * factor * 10) / 10,
      unit: nutrient.unit,
      pctDailyValue: nutrient.pctDailyValue 
        ? Math.round(nutrient.pctDailyValue * factor) 
        : undefined,
    };
  };

  return {
    ...food,
    servingSize: `${targetWeightG}g`,
    calories: Math.round(food.calories * factor),
    macros: {
      protein: scaleNutrient(food.macros.protein)!,
      fat: scaleNutrient(food.macros.fat)!,
      carbs: scaleNutrient(food.macros.carbs)!,
      fiber: scaleNutrient(food.macros.fiber),
      sugar: scaleNutrient(food.macros.sugar),
    },
    micros: food.micros ? {
      sodium: scaleNutrient(food.micros.sodium),
      potassium: scaleNutrient(food.micros.potassium),
      cholesterol: scaleNutrient(food.micros.cholesterol),
      vitaminA: scaleNutrient(food.micros.vitaminA),
      vitaminC: scaleNutrient(food.micros.vitaminC),
      calcium: scaleNutrient(food.micros.calcium),
      iron: scaleNutrient(food.micros.iron),
    } : undefined,
  };
}
