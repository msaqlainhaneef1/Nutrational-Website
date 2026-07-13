export type Goal = 'loss' | 'maintenance' | 'gain';

export interface CalorieDeficitResult {
  tdee: number;
  targetCalories: number;
  deficit: number;
  weeklyDeficit: number;
  projectedWeeklyLossKg: number;
  projectedMonthlyLossKg: number;
  daysToLose1Kg: number;
  daysToLose5Kg: number;
  daysToLose10Kg: number;
}

/**
 * Calorie deficit timeline projector.
 *
 * Uses a flat deficit (default 500 kcal/day) and projects weight loss
 * over time using the standard 7700 kcal per kg of body fat approximation.
 *
 * Note: actual weight loss is non-linear due to metabolic adaptation,
 * water weight, and glycogen changes. These numbers are an estimate.
 */
export function calculateDeficitTimeline(
  tdee: number,
  deficitKcal: number = 500,
): CalorieDeficitResult {
  const safeDeficit = Math.min(Math.max(deficitKcal, 0), 1000);
  const targetCalories = Math.max(1200, tdee - safeDeficit);
  const weeklyDeficit = safeDeficit * 7;
  const kcalPerKg = 7700;
  const projectedWeeklyLossKg = Math.round((weeklyDeficit / kcalPerKg) * 100) / 100;
  const projectedMonthlyLossKg = Math.round((projectedWeeklyLossKg * 4.33) * 100) / 100;
  const daysToLose1Kg = projectedWeeklyLossKg > 0 ? Math.round(kcalPerKg / safeDeficit) : 0;
  const daysToLose5Kg = projectedWeeklyLossKg > 0 ? Math.round((5 * kcalPerKg) / safeDeficit) : 0;
  const daysToLose10Kg = projectedWeeklyLossKg > 0 ? Math.round((10 * kcalPerKg) / safeDeficit) : 0;

  return {
    tdee,
    targetCalories,
    deficit: safeDeficit,
    weeklyDeficit,
    projectedWeeklyLossKg,
    projectedMonthlyLossKg,
    daysToLose1Kg,
    daysToLose5Kg,
    daysToLose10Kg,
  };
}
