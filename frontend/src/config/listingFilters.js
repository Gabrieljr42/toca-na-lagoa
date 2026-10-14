/**
 * Declarative description of the listing filters. Adding a filter means adding
 * an entry here (and supporting it in the API); the components just render the
 * lists.
 */

export const SELECT_FILTERS = [
  { key: 'neighborhood', label: 'Bairro', icon: 'pin', options: ({ neighborhoods }) => neighborhoods.map((name) => [name, name]) },
  { key: 'kind', label: 'Tipo', icon: 'house', options: ({ options }) => Object.entries(options.kind_labels) },
  { key: 'source', label: 'Site', icon: 'globe', options: ({ options }) => Object.entries(options.source_labels) },
];

export const TOGGLE_FILTERS = [
  { key: 'only_new', label: 'Novos 24h', icon: 'sparkle' },
  { key: 'favorites', label: 'Favoritos', icon: 'star' },
  { key: 'furnished', label: 'Mobiliado', icon: 'sofa' },
  { key: 'show_hidden', label: 'Ocultos', icon: 'eyeOff' },
  { key: 'show_inactive', label: 'Removidos', icon: 'trash' },
];

const DEFAULT_SORT = 'total';
const DESCENDING_BY_DEFAULT = new Set(['recent']);

export function defaultOrder(sort) {
  return DESCENDING_BY_DEFAULT.has(sort) ? 'desc' : 'asc';
}

export function filtersFromQuery(query) {
  const sort = query.sort || DEFAULT_SORT;
  const filters = { sort, order: query.order === 'desc' || query.order === 'asc' ? query.order : defaultOrder(sort) };
  SELECT_FILTERS.forEach(({ key }) => { filters[key] = query[key] ?? ''; });
  TOGGLE_FILTERS.forEach(({ key }) => { filters[key] = query[key] === '1'; });
  return filters;
}

export function filtersToQuery(filters) {
  const query = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value === true) query[key] = '1';
    else if (value) query[key] = value;
  }
  return query;
}

export function countActiveFilters(filters) {
  return [...SELECT_FILTERS, ...TOGGLE_FILTERS].filter(({ key }) => Boolean(filters[key])).length;
}

export function clearedFilters(filters) {
  return filtersFromQuery({ sort: filters.sort, order: filters.order });
}
