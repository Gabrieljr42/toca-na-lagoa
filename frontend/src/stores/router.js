/**
 * Minimal history-API router: the app has two pages, so a full router library
 * would add more than it saves. Query parameters are exposed so pages can keep
 * their state (e.g. filters) in the URL.
 */

import { computed, shallowRef } from 'vue';

export function createRouter(routes) {
  const path = shallowRef(location.pathname);
  const query = shallowRef(readQuery());
  const current = computed(() => routes.find((route) => route.path === path.value) ?? routes[0]);

  function sync() {
    path.value = location.pathname;
    query.value = readQuery();
  }

  function push(to) {
    if (to === location.pathname + location.search) return;
    history.pushState(null, '', to);
    sync();
    window.scrollTo({ top: 0 });
  }

  function replaceQuery(params) {
    const url = new URL(location.href);
    url.search = new URLSearchParams(params).toString();
    history.replaceState(null, '', url);
    query.value = { ...params };
  }

  window.addEventListener('popstate', sync);

  return { path, query, current, routes, push, replaceQuery };
}

function readQuery() {
  return Object.fromEntries(new URLSearchParams(location.search));
}
