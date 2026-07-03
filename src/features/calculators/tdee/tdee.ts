import { calculateBMR } from '../bmr/bmr';

export type ActivityLevel =
  | 'sedentary'
  | 'light'
  | 'moderate'
  | 'active'
  | 'extreme';

export interface MacroBreakdown {
  proteinGrams: number;
  carbGrams: number;
  fatGrams: number;
}

export interface TdeeResult {
  bmr: number;
  bmrHarris: number;
  bmrMegajoules: number;
  tdee: number;
  maintenanceCalories: number;
  weightLossCalories: number;
  weightGainCalories: number;
  waterLiters: number;
  macros: {
    balanced: MacroBreakdown;
    lowCarb: MacroBreakdown;
    keto: MacroBreakdown;
  };
}

export const activityMultipliers: Record<ActivityLevel, number> = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  extreme: 1.9,
};

const activityWaterBoosts: Record<ActivityLevel, number> = {
  sedentary: 0,
  light: 0.3,
  moderate: 0.6,
  active: 0.9,
  extreme: 1.2,
};

export function calculateTDEE(
  weightKg: number,
  heightCm: number,
  ageYears: number,
  gender: 'male' | 'female',
  activity: ActivityLevel
): TdeeResult {
  const bmrRes = calculateBMR(weightKg, heightCm, ageYears, gender);
  const multiplier = activityMultipliers[activity];
  const tdee = bmrRes.bmr * multiplier;

  // Water Intake: 35ml per kg of bodyweight + activity boost
  const baseWater = (weightKg * 35) / 1000;
  const waterLiters = baseWater + activityWaterBoosts[activity];

  // Macros Calculation helper
  const calcMacros = (cals: number, protPct: number, carbPct: number, fatPct: number): MacroBreakdown => {
    return {
      proteinGrams: Math.round((cals * protPct) / 4),
      carbGrams: Math.round((cals * carbPct) / 4),
      fatGrams: Math.round((cals * fatPct) / 9),
    };
  };

  return {
    bmr: bmrRes.bmr,
    bmrHarris: bmrRes.bmrHarris,
    bmrMegajoules: bmrRes.bmrMegajoules,
    tdee: Math.round(tdee),
    maintenanceCalories: Math.round(tdee),
    weightLossCalories: Math.round(tdee - 500),
    weightGainCalories: Math.round(tdee + 500),
    waterLiters: Math.round(waterLiters * 10) / 10,
    macros: {
      balanced: calcMacros(tdee, 0.30, 0.40, 0.30),
      lowCarb: calcMacros(tdee, 0.40, 0.30, 0.30),
      keto: calcMacros(tdee, 0.20, 0.05, 0.75),
    },
  };
}
