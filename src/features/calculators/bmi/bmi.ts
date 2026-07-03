export interface BmiResult {
  bmi: number;
  category: 'Underweight' | 'Normal weight' | 'Overweight' | 'Obese';
  minHealthyWeight: number;
  maxHealthyWeight: number;
  ponderalIndex: number;
  bmiPrime: number;
  bodyFatPct: number;
}

export function calculateBMI(
  weightKg: number,
  heightCm: number,
  ageYears?: number,
  gender?: 'male' | 'female'
): BmiResult {
  const heightM = heightCm / 100;
  const bmi = weightKg / (heightM * heightM);

  let category: BmiResult['category'] = 'Normal weight';
  if (bmi < 18.5) {
    category = 'Underweight';
  } else if (bmi < 25) {
    category = 'Normal weight';
  } else if (bmi < 30) {
    category = 'Overweight';
  } else {
    category = 'Obese';
  }

  const minHealthyWeight = 18.5 * (heightM * heightM);
  const maxHealthyWeight = 24.9 * (heightM * heightM);

  // Ponderal Index: weight / height^3
  const ponderalIndex = weightKg / (heightM * heightM * heightM);

  // BMI Prime: actual BMI / upper limit of normal BMI (25)
  const bmiPrime = bmi / 25;

  // Body Fat Percentage (adult formula)
  const age = ageYears || 25;
  const isMale = gender === 'male' || !gender;
  const genderFactor = isMale ? 1 : 0;
  const bodyFatPct = (1.20 * bmi) + (0.23 * age) - (10.8 * genderFactor) - 5.4;

  return {
    bmi: Math.round(bmi * 10) / 10,
    category,
    minHealthyWeight: Math.round(minHealthyWeight * 10) / 10,
    maxHealthyWeight: Math.round(maxHealthyWeight * 10) / 10,
    ponderalIndex: Math.round(ponderalIndex * 10) / 10,
    bmiPrime: Math.round(bmiPrime * 100) / 100,
    bodyFatPct: Math.round(Math.max(2, bodyFatPct) * 10) / 10,
  };
}
