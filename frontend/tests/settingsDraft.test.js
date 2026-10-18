import { describe, expect, it } from 'vitest';
import { toDraft, toPayload } from '../src/core/settingsDraft.js';

const SETTINGS = {
  enabled: true,
  neighborhoods: ['Castelo'],
  max_bedrooms: 1,
  check_times: ['08:00'],
  max_area: 70,
  min_total: null,
  max_total: 2500,
  sale_enabled: true,
  sale_max_bedrooms: 2,
  sale_max_area: null,
  sale_min_price: null,
  sale_max_price: 450000,
  sale_max_monthly: 3500,
  financing_down_payment_percent: 20,
  financing_rate: 11.5,
  financing_term_years: 30,
  financing_system: 'sac',
};

describe('settings draft', () => {
  it('shows optional numbers as formatted text', () => {
    expect(toDraft(SETTINGS)).toMatchObject({ max_total: '2.500', min_total: '', sale_max_price: '450.000', financing_rate: '11,5' });
  });

  it('turns the draft back into the API payload', () => {
    expect(toPayload(toDraft(SETTINGS)).value).toEqual(SETTINGS);
  });

  it('reports a field typed with letters', () => {
    expect(toPayload({ ...toDraft(SETTINGS), min_total: '1k' }).error).toMatch('Valor mínimo');
  });

  it('accepts the interest rate with a dot or a comma', () => {
    expect(toPayload({ ...toDraft(SETTINGS), financing_rate: '10.99' }).value.financing_rate).toBe(10.99);
    expect(toPayload({ ...toDraft(SETTINGS), financing_rate: '12,25%' }).value.financing_rate).toBe(12.25);
  });

  it('requires a valid interest rate', () => {
    expect(toPayload({ ...toDraft(SETTINGS), financing_rate: '' }).error).toMatch('Juros');
    expect(toPayload({ ...toDraft(SETTINGS), financing_rate: 'doze' }).error).toMatch('Juros');
  });
});
