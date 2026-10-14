/**
 * Minimal history-API router: the app has a handful of pages, so a full router
 * library would add more than it saves. Query parameters are exposed so pages
 * can keep their state (e.g. filters) in the URL. A guard (set by the
 * composition root) may redirect any navigation, e.g. to the login page.
 */

import { computed, shallowRef } from 'vue';

export function createRouter(routes) {
  const path = shallowRef(location.pathname);
  const query = shallowRef(readQuery());
  const current = computed(() => routes.find((route) => route.path === path.value) ?? routes[0]);
  let guard = () => null;

  function sync() {
    path.value = location.pathname;
    query.value = readQuery();
  }

  function push(to) {
    const target = guard(new URL(to, location.origin)) ?? to;
    if (target === currentUrl()) return;
    history.pushState(null, '', target);
    sync();
    window.scrollTo({ top: 0 });
  }

  function setGuard(callback) {
    guard = callback;
    revalidate();
  }

  /** Re-apply the guard to the current URL (e.g. after logging in or out). */
  function revalidate() {
    const target = guard(new URL(location.href));
    if (target && target !== currentUrl()) {
      history.replaceState(null, '', target);
      sync();
    }
  }

  function replaceQuery(params) {
    const url = new URL(location.href);
    url.search = new URLSearchParams(params).toString();
    history.replaceState(null, '', url);
    query.value = { ...params };
  }

  window.addEventListener('popstate', () => {
    sync();
    revalidate();
  });

  return { path, query, current, routes, push, replaceQuery, setGuard, revalidate };
}

function currentUrl() {
  return location.pathname + location.search;
}

function readQuery() {
  return Object.fromEntries(new URLSearchParams(location.search));
}
