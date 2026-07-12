import { calculateBMR } from '../bmr/bmr';

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
  weightLossCalories: number;
  weightGainCalories: number;
}

export const activityMultipliers: Record<ActivityLevel, number> = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  extreme: 1.9,
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
