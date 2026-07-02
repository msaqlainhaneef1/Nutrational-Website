export interface BmiResult {
  bmi: number;
  category: 'Underweight' | 'Normal weight' | 'Overweight' | 'Obese';
  minHealthyWeight: number; // in kg
  maxHealthyWeight: number; // in kg
}

export function calculateBMI(weightKg: number, heightCm: number): BmiResult {
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

  return {
    bmi: Math.round(bmi * 10) / 10,
    category,
    minHealthyWeight: Math.round(minHealthyWeight * 10) / 10,
    maxHealthyWeight: Math.round(maxHealthyWeight * 10) / 10,
  };
}
