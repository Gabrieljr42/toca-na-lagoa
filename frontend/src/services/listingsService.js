/** Listings endpoints. */

import { filtersToQuery } from '../config/listingFilters.js';

export class ListingsService {
  constructor(http) {
    this.http = http;
  }

  /** Listings of one business ('rent' or 'sale'); the business comes from the page, not the URL query. */
  list(business, filters) {
    return this.http.get('/api/listings', { business, ...filtersToQuery(filters) });
  }

  update(listingId, changes) {
    return this.http.patch(`/api/listings/${listingId}`, changes);
  }

  favoritesSummary() {
    return this.http.get('/api/favorites/summary');
  }
}
