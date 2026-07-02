export type FitnessGoal = 'loss' | 'maintenance' | 'gain';

export interface ProteinResult {
  proteinGrams: number;
  proteinPerKg: number;
}

export function calculateProtein(
  weightKg: number,
  goal: FitnessGoal,
  activityMultiplier: number // 1.2 to 1.9, matching TDEE multipliers
): ProteinResult {
  let proteinPerKg = 1.2;

  // Base allocation by activity multiplier
  if (activityMultiplier < 1.3) {
    proteinPerKg = 1.0;
  } else if (activityMultiplier < 1.5) {
    proteinPerKg = 1.4;
  } else if (activityMultiplier < 1.7) {
    proteinPerKg = 1.8;
  } else {
    proteinPerKg = 2.2;
  }

  // Adjustments based on goal
  if (goal === 'loss') {
    // Deficit requires higher protein intake to preserve muscle tissue
    proteinPerKg = Math.max(1.6, proteinPerKg + 0.2);
  } else if (goal === 'gain') {
    // Hypertrophy/surplus targets
    proteinPerKg = Math.max(1.8, proteinPerKg + 0.1);
  }

  return {
    proteinGrams: Math.round(weightKg * proteinPerKg),
    proteinPerKg,
  };
}
