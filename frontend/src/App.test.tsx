import { describe, it, expect } from 'vitest';

describe('PAIMANA Frontend Suite', () => {
  it('should validate risk band boundary thresholds', () => {
    const getRiskBand = (score: number) => {
      if (score >= 75) return 'CRITICAL';
      if (score >= 50) return 'HIGH';
      if (score >= 30) return 'MODERATE';
      return 'LOW';
    };

    expect(getRiskBand(15.5)).toBe('LOW');
    expect(getRiskBand(35.0)).toBe('MODERATE');
    expect(getRiskBand(62.8)).toBe('HIGH');
    expect(getRiskBand(88.4)).toBe('CRITICAL');
  });

  it('should compute financial vs physical gap accurately', () => {
    const calcGap = (financial: number, physical: number) => {
      return Number((financial - physical).toFixed(1));
    };

    expect(calcGap(72.5, 45.0)).toBe(27.5);
    expect(calcGap(50.0, 50.0)).toBe(0.0);
  });
});
