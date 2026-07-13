export type Gender = 'male' | 'female';
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'extreme';
export type Goal = 'loss' | 'maintenance' | 'gain';
export type DietApproach = 'balanced' | 'high-protein' | 'low-carb' | 'keto';

export interface MacroResult {
  bmr: number;
  tdee: number;
  targetCalories: number;
  proteinGrams: number;
  carbGrams: number;
  fatGrams: number;
  proteinPct: number;
  carbPct: number;
  fatPct: number;
  proteinPerKg: number;
}

export const activityMultipliers: Record<ActivityLevel, number> = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  extreme: 1.9,
};

export function calculateBMR(weightKg: number, heightCm: number, ageYears: number, gender: Gender): number {
  const base = 10 * weightKg + 6.25 * heightCm - 5 * ageYears;
  return Math.round(gender === 'male' ? base + 5 : base - 161);
}

const macroSplits: Record<DietApproach, { protein: number; carbs: number; fat: number }> = {
  balanced: { protein: 0.3, carbs: 0.4, fat: 0.3 },
  'high-protein': { protein: 0.4, carbs: 0.35, fat: 0.25 },
  'low-carb': { protein: 0.35, carbs: 0.2, fat: 0.45 },
  keto: { protein: 0.25, carbs: 0.05, fat: 0.7 },
};

const goalAdjustments: Record<Goal, number> = {
  loss: -500,
  maintenance: 0,
  gain: 350,
};

export function calculateMacro(
  weightKg: number,
  heightCm: number,
  ageYears: number,
  gender: Gender,
  activity: ActivityLevel,
  goal: Goal,
  diet: DietApproach
): MacroResult {
  const bmr = calculateBMR(weightKg, heightCm, ageYears, gender);
  const tdee = Math.round(bmr * activityMultipliers[activity]);
  const targetCalories = Math.max(1200, tdee + goalAdjustments[goal]);

  const split = macroSplits[diet];
  const proteinGrams = Math.round((targetCalories * split.protein) / 4);
  const carbGrams = Math.round((targetCalories * split.carbs) / 4);
  const fatGrams = Math.round((targetCalories * split.fat) / 9);

  return {
    bmr,
    tdee,
    targetCalories,
    proteinGrams,
    carbGrams,
    fatGrams,
    proteinPct: Math.round(split.protein * 100),
    carbPct: Math.round(split.carbs * 100),
    fatPct: Math.round(split.fat * 100),
    proteinPerKg: Math.round((proteinGrams / weightKg) * 10) / 10,
  };
}

export function defaultMacroTargets(tdee: number) {
  return {
    protein: Math.round((tdee * 0.3) / 4),
    carbs: Math.round((tdee * 0.4) / 4),
    fat: Math.round((tdee * 0.3) / 9),
    calories: tdee,
  };
}
