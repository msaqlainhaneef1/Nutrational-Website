export interface BmrResult {
  bmr: number; // Mifflin-St Jeor (default)
  bmrHarris: number; // Revised Harris-Benedict
  bmrMegajoules: number; // in MJ/day
}

export function calculateBMR(
  weightKg: number,
  heightCm: number,
  ageYears: number,
  gender: 'male' | 'female'
): BmrResult {
  // 1. Mifflin-St Jeor
  let bmrMifflin = 0;
  if (gender === 'male') {
    bmrMifflin = 10 * weightKg + 6.25 * heightCm - 5 * ageYears + 5;
  } else {
    bmrMifflin = 10 * weightKg + 6.25 * heightCm - 5 * ageYears - 161;
  }

  // 2. Revised Harris-Benedict
  let bmrHarris = 0;
  if (gender === 'male') {
    bmrHarris = 13.397 * weightKg + 4.799 * heightCm - 5.677 * ageYears + 88.362;
  } else {
    bmrHarris = 9.247 * weightKg + 3.098 * heightCm - 4.330 * ageYears + 447.593;
  }

  // Convert kcal to Megajoules (1 kcal = 0.004184 MJ)
  const bmrMegajoules = bmrMifflin * 0.004184;

  return {
    bmr: Math.round(bmrMifflin),
    bmrHarris: Math.round(bmrHarris),
    bmrMegajoules: Math.round(bmrMegajoules * 100) / 100,
  };
}
