import { calculateBMR } from './bmr';

export type ActivityLevel =
  | 'sedentary'
  | 'light'
  | 'moderate'
  | 'active'
  | 'extreme';

export interface TdeeResult {
  bmr: number;
  tdee: number;
  maintenanceCalories: number;
  weightLossCalories: number; // -500 kcal deficit
  weightGainCalories: number; // +500 kcal surplus
}

export const activityMultipliers: Record<ActivityLevel, number> = {
  sedentary: 1.2,      // Desk job, little/no exercise
  light: 1.375,        // Light exercise 1-3 days/week
  moderate: 1.55,      // Moderate exercise 3-5 days/week
  active: 1.725,       // Hard exercise 6-7 days/week
  extreme: 1.9,        // Heavy physical job or 2x daily training
};

export function calculateTDEE(
  weightKg: number,
  heightCm: number,
  ageYears: number,
  gender: 'male' | 'female',
  activity: ActivityLevel
): TdeeResult {
  const { bmr } = calculateBMR(weightKg, heightCm, ageYears, gender);
  const multiplier = activityMultipliers[activity];
  const tdee = bmr * multiplier;

  return {
    bmr,
    tdee: Math.round(tdee),
    maintenanceCalories: Math.round(tdee),
    weightLossCalories: Math.round(tdee - 500),
    weightGainCalories: Math.round(tdee + 500),
  };
}
