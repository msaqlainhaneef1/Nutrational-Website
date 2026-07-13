/**
 * Central registry of all calculators on Nutrition Solver.
 * Used by the calculators directory, mega-menu, and homepage.
 */

import type { Component } from 'astro';

export interface CalculatorMeta {
  slug: string;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
  category: CalculatorCategory;
  icon: string; // emoji
  accent: string; // tailwind color classes
  popular?: boolean;
}

export type CalculatorCategory =
  | 'Body Composition'
  | 'Energy & Calories'
  | 'Macros & Diet'
  | 'Micronutrients'
  | 'Fitness & Performance';

export const CALCULATORS: CalculatorMeta[] = [
  // Body Composition
  {
    slug: 'bmi',
    name: 'BMI Calculator',
    shortName: 'BMI',
    tagline: 'Body Mass Index',
    description: 'Quick weight category check based on height and weight. Returns BMI score, category, and healthy weight range.',
    category: 'Body Composition',
    icon: '⚖️',
    accent: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    popular: true,
  },
  {
    slug: 'body-fat',
    name: 'Body Fat Calculator',
    shortName: 'Body Fat',
    tagline: 'U.S. Navy method',
    description: 'Body fat percentage from circumference measurements using the U.S. Navy protocol. Returns body fat percent and category.',
    category: 'Body Composition',
    icon: '🧮',
    accent: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
  },
  {
    slug: 'ideal-weight',
    name: 'Ideal Weight Calculator',
    shortName: 'Ideal Weight',
    tagline: 'Devine, Robinson, Miller, Hamwi',
    description: 'Healthy weight range using four classic clinical formulas, adjusted for body frame size.',
    category: 'Body Composition',
    icon: '📏',
    accent: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  },

  // Energy & Calories
  {
    slug: 'bmr',
    name: 'BMR Calculator',
    shortName: 'BMR',
    tagline: 'Basal Metabolic Rate',
    description: 'Calories your body burns at complete rest using the Mifflin-St Jeor equation. The foundation of any meal plan.',
    category: 'Energy & Calories',
    icon: '🔥',
    accent: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    popular: true,
  },
  {
    slug: 'tdee',
    name: 'TDEE Calculator',
    shortName: 'TDEE',
    tagline: 'Total Daily Energy Expenditure',
    description: 'Daily maintenance calories based on activity level. Includes cut and bulk targets for goal-specific planning.',
    category: 'Energy & Calories',
    icon: '⚡',
    accent: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    popular: true,
  },
  {
    slug: 'calorie-deficit',
    name: 'Calorie Deficit Calculator',
    shortName: 'Calorie Deficit',
    tagline: 'Weight loss timeline',
    description: 'Project weight loss timeline from your daily deficit. Shows weeks to lose 1, 5, and 10 kg based on your TDEE.',
    category: 'Energy & Calories',
    icon: '📉',
    accent: 'text-red-400 bg-red-500/10 border-red-500/20',
    popular: true,
  },

  // Macros & Diet
  {
    slug: 'macro',
    name: 'Macro Calculator',
    shortName: 'Macros',
    tagline: 'Protein, carbs, fat split',
    description: 'Daily protein, carb, and fat targets based on your TDEE, goal, and preferred diet approach (balanced, high protein, low carb, keto).',
    category: 'Macros & Diet',
    icon: '🎯',
    accent: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    popular: true,
  },
  {
    slug: 'protein',
    name: 'Protein Calculator',
    shortName: 'Protein',
    tagline: 'Daily protein target',
    description: 'Daily protein intake in grams based on body weight, activity level, and fitness goal.',
    category: 'Macros & Diet',
    icon: '🥩',
    accent: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
  },
  {
    slug: 'water-intake',
    name: 'Water Intake Calculator',
    shortName: 'Water Intake',
    tagline: 'Daily hydration target',
    description: 'Daily water requirement in liters, ounces, and glasses based on body weight, activity, and climate.',
    category: 'Macros & Diet',
    icon: '💧',
    accent: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  },
];

export const CALCULATOR_CATEGORIES: { name: CalculatorCategory; description: string }[] = [
  { name: 'Body Composition', description: 'BMI, body fat, and ideal weight tools.' },
  { name: 'Energy & Calories', description: 'BMR, TDEE, and weight loss timeline.' },
  { name: 'Macros & Diet', description: 'Macro split, protein, and hydration targets.' },
];

export function getCalculatorsByCategory(category: CalculatorCategory): CalculatorMeta[] {
  return CALCULATORS.filter((c) => c.category === category);
}

export function getPopularCalculators(limit: number = 4): CalculatorMeta[] {
  return CALCULATORS.filter((c) => c.popular).slice(0, limit);
}

export function getCalculatorBySlug(slug: string): CalculatorMeta | undefined {
  return CALCULATORS.find((c) => c.slug === slug);
}
