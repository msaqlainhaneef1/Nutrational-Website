import { z } from 'zod';

export const MenuItemSchema = z.object({
  name: z.string(),
  servingSize: z.string().optional(),
  calories: z.number(),
  protein: z.number(), // in grams
  fat: z.number(),     // in grams
  carbs: z.number(),   // in grams
  fiber: z.number().optional(), // in grams
  sodium: z.number().optional(), // in mg
});

export const MenuCategorySchema = z.object({
  name: z.string(),
  items: z.array(MenuItemSchema),
});

export const RestaurantSchema = z.object({
  name: z.string(),
  slug: z.string(),
  description: z.string().optional(),
  logo: z.string().optional(),
  categories: z.array(MenuCategorySchema),
});

export type Restaurant = z.infer<typeof RestaurantSchema>;
export type MenuItem = z.infer<typeof MenuItemSchema>;
