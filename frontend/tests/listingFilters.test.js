import { describe, expect, it } from 'vitest';
import { clearedFilters, countActiveFilters, filtersFromQuery, filtersToQuery } from '../src/config/listingFilters.js';

describe('listing filters', () => {
  it('defaults to cheapest first and newest first for "recent"', () => {
    expect(filtersFromQuery({}).order).toBe('asc');
    expect(filtersFromQuery({ sort: 'recent' }).order).toBe('desc');
  });

  it('round-trips through the URL query keeping only active filters', () => {
    const filters = filtersFromQuery({ sort: 'area', favorites: '1', neighborhood: 'Castelo' });
    expect(filtersToQuery(filters)).toEqual({ sort: 'area', order: 'asc', favorites: '1', neighborhood: 'Castelo' });
  });

  it('counts and clears filters but keeps the ordering', () => {
    const filters = filtersFromQuery({ sort: 'rent', order: 'desc', favorites: '1', kind: 'studio' });
    expect(countActiveFilters(filters)).toBe(2);
    const cleared = clearedFilters(filters);
    expect(countActiveFilters(cleared)).toBe(0);
    expect([cleared.sort, cleared.order]).toEqual(['rent', 'desc']);
  });
});
