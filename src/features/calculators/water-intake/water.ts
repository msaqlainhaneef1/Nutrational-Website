export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'extreme';
export type Climate = 'temperate' | 'hot' | 'cold';

export interface WaterResult {
  baseLiters: number;
  adjustedLiters: number;
  adjustedOz: number;
  glasses: number;
  recommendation: string;
}

/**
 * Daily water intake based on body weight and activity.
 *
 * Rule of thumb: 35 ml per kg of body weight.
 * Activity adds 0.35 to 1.0 liters depending on intensity.
 * Hot climate adds 0.5 L, cold adds 0.3 L (cold diuresis is real).
 */
export function calculateWater(
  weightKg: number,
  activity: ActivityLevel,
  climate: Climate = 'temperate'
): WaterResult {
  const baseMl = weightKg * 35;
  const baseLiters = Math.round((baseMl / 1000) * 10) / 10;

  const activityAddition = {
    sedentary: 0,
    light: 0.35,
    moderate: 0.5,
    active: 0.7,
    extreme: 1.0,
  }[activity];

  const climateAddition = { temperate: 0, hot: 0.5, cold: 0.3 }[climate];

  const adjustedLiters = Math.round((baseLiters + activityAddition + climateAddition) * 10) / 10;
  const adjustedOz = Math.round(adjustedLiters * 33.814);
  const glasses = Math.round((adjustedLiters * 1000) / 250);

  let recommendation: string;
  if (adjustedLiters < 2) {
    recommendation = 'Light hydration needs. Sip steadily through the day rather than drinking large amounts at once.';
  } else if (adjustedLiters < 3) {
    recommendation = 'Moderate hydration. Keep a 750 ml bottle within reach and refill it three to four times.';
  } else if (adjustedLiters < 4) {
    recommendation = 'Above average hydration. Spread intake across the day and include electrolyte rich foods if you sweat heavily.';
  } else {
    recommendation = 'High hydration needs, typical for athletes or hot climates. Drink to thirst and monitor urine color as a quick check.';
  }

  return { baseLiters, adjustedLiters, adjustedOz, glasses, recommendation };
}
