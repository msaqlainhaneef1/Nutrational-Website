export interface BodyFatResult {
  bodyFatPercentage: number;
  category: 'Essential fat' | 'Athletes' | 'Fitness' | 'Average' | 'Obese';
}

export function calculateBodyFat(
  gender: 'male' | 'female',
  heightCm: number,
  waistCm: number,
  neckCm: number,
  hipCm?: number // Required for females
): BodyFatResult {
  let bfp = 0;

  if (gender === 'male') {
    // US Navy formula for men (metric)
    const logVal = Math.log10(waistCm - neckCm);
    const logHeight = Math.log10(heightCm);
    const density = 1.0324 - 0.19077 * logVal + 0.15456 * logHeight;
    bfp = 495 / density - 450;
  } else {
    // US Navy formula for women (metric)
    const hip = hipCm || 0;
    const logVal = Math.log10(waistCm + hip - neckCm);
    const logHeight = Math.log10(heightCm);
    const density = 1.29579 - 0.35004 * logVal + 0.22100 * logHeight;
    bfp = 495 / density - 450;
  }

  // Cap value
  bfp = Math.max(2, Math.min(60, Math.round(bfp * 10) / 10));

  let category: BodyFatResult['category'] = 'Average';
  if (gender === 'male') {
    if (bfp < 6) category = 'Essential fat';
    else if (bfp < 14) category = 'Athletes';
    else if (bfp < 18) category = 'Fitness';
    else if (bfp < 25) category = 'Average';
    else category = 'Obese';
  } else {
    if (bfp < 14) category = 'Essential fat';
    else if (bfp < 21) category = 'Athletes';
    else if (bfp < 25) category = 'Fitness';
    else if (bfp < 32) category = 'Average';
    else category = 'Obese';
  }

  return {
    bodyFatPercentage: bfp,
    category,
  };
}
