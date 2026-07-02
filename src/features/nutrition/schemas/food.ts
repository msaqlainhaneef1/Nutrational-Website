import { z } from 'zod';

export const NutrientSchema = z.object({
  value: z.number(),
  unit: z.string(),
  pctDailyValue: z.number().optional(),
});

export const FoodSchema = z.object({
  name: z.string(),
  slug: z.string(),
  description: z.string().optional(),
  category: z.string(),
  servingSize: z.string(),
  calories: z.number(),
  macros: z.object({
    protein: NutrientSchema,
    fat: NutrientSchema,
    carbs: NutrientSchema,
    fiber: NutrientSchema.optional(),
    sugar: NutrientSchema.optional(),
  }),
  micros: z.object({
    sodium: NutrientSchema.optional(),
    potassium: NutrientSchema.optional(),
    cholesterol: NutrientSchema.optional(),
    vitaminA: NutrientSchema.optional(),
    vitaminC: NutrientSchema.optional(),
    calcium: NutrientSchema.optional(),
    iron: NutrientSchema.optional(),
  }).optional(),
  faqs: z.array(z.object({
    q: z.string(),
    a: z.string(),
  })).optional(),
});

export type Food = z.infer<typeof FoodSchema>;
export type Nutrient = z.infer<typeof NutrientSchema>;
