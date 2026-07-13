export type Gender = 'male' | 'female';
export type BodyFrame = 'small' | 'medium' | 'large';

export interface IdealWeightResult {
  devine: number;
  robinson: number;
  miller: number;
  hamwi: number;
  healthyRange: { min: number; max: number };
  average: number;
}

/**
 * Compute ideal body weight using four classic formulas.
 * All formulas are based on height in inches above 5 feet (60 inches).
 * Input is height in centimeters.
 */
export function calculateIdealWeight(heightCm: number, gender: Gender, frame: BodyFrame): IdealWeightResult {
  const heightInches = heightCm / 2.54;
  const inchesOver5Ft = Math.max(0, heightInches - 60);

  // Devine (1974) - the most widely used, originally for drug dosing
  const devineBase = gender === 'male' ? 50 : 45.5;
  const devine = devineBase + 2.3 * inchesOver5Ft;

  // Robinson (1983)
  const robinsonBase = gender === 'male' ? 52 : 49;
  const robinson = robinsonBase + (gender === 'male' ? 1.9 : 1.7) * inchesOver5Ft;

  // Miller (1983)
  const millerBase = gender === 'male' ? 56.2 : 53.1;
  const miller = millerBase + (gender === 'male' ? 1.41 : 1.36) * inchesOver5Ft;

  // Hamwi (1964)
  const hamwiBase = gender === 'male' ? 48 : 45.4;
  const hamwi = hamwiBase + (gender === 'male' ? 2.7 : 2.2) * inchesOver5Ft;

  // Healthy BMI range 18.5 to 24.9
  const heightM = heightCm / 100;
  const healthyRange = {
    min: Math.round(18.5 * heightM * heightM * 10) / 10,
    max: Math.round(24.9 * heightM * heightM * 10) / 10,
  };

  // Frame adjustment: small frame subtract 10%, large frame add 10%
  const frameMultiplier = frame === 'small' ? 0.9 : frame === 'large' ? 1.1 : 1;
  const average = Math.round(((devine + robinson + miller + hamwi) / 4) * frameMultiplier * 10) / 10;

  return {
    devine: Math.round(devine * 10) / 10,
    robinson: Math.round(robinson * 10) / 10,
    miller: Math.round(miller * 10) / 10,
    hamwi: Math.round(hamwi * 10) / 10,
    healthyRange,
    average,
  };
}
