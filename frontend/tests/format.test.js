import { describe, expect, it } from 'vitest';
import { formatBrl, formatDateTime, normalizeText, parseInteger } from '../src/core/format.js';

describe('format', () => {
  it('formats whole reais in pt-BR', () => {
    expect(formatBrl(2500)).toBe('R$ 2.500');
    expect(formatBrl(null)).toBe('—');
  });

  it('reads naive timestamps without shifting the timezone', () => {
    expect(formatDateTime('2026-10-13T15:41:32.383986')).toBe('13/10 às 15:41');
  });

  it('parses typed money, treating blank as no limit', () => {
    expect(parseInteger('R$ 2.500')).toBe(2500);
    expect(parseInteger('')).toBeNull();
    expect(parseInteger('abc')).toBeNaN();
  });

  it('compares neighborhoods ignoring accents and case', () => {
    expect(normalizeText('  São   Luíz ')).toBe(normalizeText('sao luiz'));
  });
});
