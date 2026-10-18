/**
 * Conversion between the settings returned by the API and the editable form
 * draft, where optional numbers are kept as the text the user typed.
 */

import { formatDecimal, formatNumber, parseDecimal, parseInteger } from './format.js';

const PLAIN_FIELDS = [
  'enabled',
  'max_bedrooms',
  'sale_enabled',
  'sale_max_bedrooms',
  'financing_down_payment_percent',
  'financing_term_years',
  'financing_system',
];
const LIST_FIELDS = ['neighborhoods', 'check_times'];
const OPTIONAL_NUMBERS = {
  max_area: 'Área máxima',
  min_total: 'Valor mínimo',
  max_total: 'Valor máximo',
  sale_max_area: 'Área máxima da compra',
  sale_min_price: 'Preço mínimo',
  sale_max_price: 'Preço máximo',
  sale_max_monthly: 'Custo mensal máximo',
};

export function toDraft(settings) {
  return {
    ...Object.fromEntries(PLAIN_FIELDS.map((key) => [key, settings[key]])),
    ...Object.fromEntries(LIST_FIELDS.map((key) => [key, [...settings[key]]])),
    ...Object.fromEntries(Object.keys(OPTIONAL_NUMBERS).map((key) => [key, formatNumber(settings[key])])),
    financing_rate: formatDecimal(settings.financing_rate),
  };
}

/** Returns `{ value }` ready for the API, or `{ error }` with a message for the user. */
export function toPayload(draft) {
  const value = {
    ...Object.fromEntries(PLAIN_FIELDS.map((key) => [key, draft[key]])),
    ...Object.fromEntries(LIST_FIELDS.map((key) => [key, draft[key]])),
  };
  for (const [key, label] of Object.entries(OPTIONAL_NUMBERS)) {
    const number = parseInteger(draft[key]);
    if (Number.isNaN(number)) return { error: `${label} inválido(a): use só números.` };
    value[key] = number;
  }
  const rate = parseDecimal(draft.financing_rate);
  if (rate === null || Number.isNaN(rate)) return { error: 'Juros inválidos: use um número, como 11,5.' };
  value.financing_rate = rate;
  return { value };
}
