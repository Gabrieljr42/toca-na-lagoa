/**
 * Navigation rule tying the router to the login state: logged-out users go to
 * the login page (remembering where they were heading), logged-in users skip it.
 */

export const LOGIN_PATH = '/login';

export function createAuthGuard(auth) {
  return (url) => {
    if (!auth.checked.value) return null;
    const isLogin = url.pathname === LOGIN_PATH;
    if (!auth.authenticated.value && !isLogin) {
      return `${LOGIN_PATH}?next=${encodeURIComponent(url.pathname + url.search)}`;
    }
    if (auth.authenticated.value && isLogin) return safeNext(url.searchParams.get('next'));
    return null;
  };
}

/** Only same-app paths are accepted, so a crafted link cannot redirect elsewhere. */
function safeNext(next) {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/';
}
