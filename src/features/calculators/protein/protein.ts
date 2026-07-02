export type FitnessGoal = 'loss' | 'maintenance' | 'gain';

export interface ProteinResult {
  proteinGrams: number;
  proteinPerKg: number;
}

export function calculateProtein(
  weightKg: number,
  goal: FitnessGoal,
  activityMultiplier: number
): ProteinResult {
  let proteinPerKg = 1.2;

  if (activityMultiplier < 1.3) {
    proteinPerKg = 1.0;
  } else if (activityMultiplier < 1.5) {
    proteinPerKg = 1.4;
  } else if (activityMultiplier < 1.7) {
    proteinPerKg = 1.8;
  } else {
    proteinPerKg = 2.2;
  }

  if (goal === 'loss') {
    proteinPerKg = Math.max(1.6, proteinPerKg + 0.2);
  } else if (goal === 'gain') {
    proteinPerKg = Math.max(1.8, proteinPerKg + 0.1);
  }

  return {
    proteinGrams: Math.round(weightKg * proteinPerKg),
    proteinPerKg,
  };
}
