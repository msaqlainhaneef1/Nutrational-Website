export type FitnessGoal = 'loss' | 'maintenance' | 'gain';
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'extreme';

export interface ProteinResult {
  proteinGrams: number;
  proteinPerKg: number;
  lowEnd: number;
  highEnd: number;
  recommendation: string;
}

const activityMultipliers: Record<ActivityLevel, number> = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  active: 1.725,
  extreme: 1.9,
};

/**
 * Daily protein target based on body weight, goal, and activity.
 *
 * Activity sets the baseline protein per kg of body weight:
 *   sedentary: 0.8 g/kg (RDA minimum)
 *   light:     1.2 g/kg
 *   moderate:  1.6 g/kg
 *   active:    2.0 g/kg
 *   extreme:   2.4 g/kg
 *
 * Goal then adjusts:
 *   loss:        +0.4 g/kg (preserves lean mass in a deficit)
 *   maintenance: 0
 *   gain:        +0.2 g/kg (supports muscle protein synthesis)
 */
export function calculateProtein(
  weightKg: number,
  goal: FitnessGoal,
  activity: ActivityLevel
): ProteinResult {
  const baseProteinPerKg: Record<ActivityLevel, number> = {
    sedentary: 0.8,
    light: 1.2,
    moderate: 1.6,
    active: 2.0,
    extreme: 2.4,
  };

  let proteinPerKg = baseProteinPerKg[activity];

  if (goal === 'loss') proteinPerKg += 0.4;
  else if (goal === 'gain') proteinPerKg += 0.2;

  // Round to 1 decimal
  proteinPerKg = Math.round(proteinPerKg * 10) / 10;

  const proteinGrams = Math.round(weightKg * proteinPerKg);
  const lowEnd = Math.round(weightKg * Math.max(0.8, proteinPerKg - 0.3));
  const highEnd = Math.round(weightKg * (proteinPerKg + 0.3));

  let recommendation: string;
  if (goal === 'loss') {
    recommendation = 'When losing weight, protein preserves lean mass and keeps you full. Aim for the high end of your range on training days.';
  } else if (goal === 'gain') {
    recommendation = 'For muscle gain, spread your protein across 4 to 5 meals of 20 to 40 grams each to maximize muscle protein synthesis.';
  } else {
    recommendation = 'For maintenance, the RDA of 0.8 g/kg is the minimum to prevent deficiency. Most active adults benefit from 1.2 to 1.6 g/kg.';
  }

  return { proteinGrams, proteinPerKg, lowEnd, highEnd, recommendation };
}

export function getActivityMultiplier(activity: ActivityLevel): number {
  return activityMultipliers[activity];
}
