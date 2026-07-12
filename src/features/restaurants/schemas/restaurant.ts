import { z } from 'zod';

export const MenuItemSchema = z.object({
  name: z.string(),
  servingSize: z.string().optional(),
  calories: z.number(),
  protein: z.number(),
  fat: z.number(),
  carbs: z.number(),
  fiber: z.number().optional(),
  sodium: z.number().optional(),
  cholesterol: z.number().optional(),
  saturated_fat: z.number().optional(),
  sugars: z.number().optional(),
  trans_fat: z.number().optional(),
});

export const MenuCategorySchema = z.object({
  name: z.string(),
  items: z.array(MenuItemSchema),
});

export const RestaurantSchema = z.object({
  name: z.string(),
  slug: z.string(),
  tagline: z.string().optional(),
  description: z.string().optional(),
  category: z.string().optional(),
  emoji: z.string().optional(),
  itemCount: z.number().optional(),
  logo: z.string().optional(),
  categories: z.array(MenuCategorySchema),
});

export type Restaurant = z.infer<typeof RestaurantSchema>;
export type MenuItem = z.infer<typeof MenuItemSchema>;
export type MenuCategory = z.infer<typeof MenuCategorySchema>;
