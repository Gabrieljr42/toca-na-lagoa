/**
 * Login state. Other parts of the app subscribe to sign-in/sign-out instead of
 * checking the session themselves.
 */

import { ref } from 'vue';

export function createAuthStore(authService) {
  const checked = ref(false);
  const authenticated = ref(false);
  const passwordRequired = ref(true);
  const listeners = { signedIn: new Set(), signedOut: new Set() };

  function apply(session) {
    const wasAuthenticated = authenticated.value;
    authenticated.value = session.authenticated;
    passwordRequired.value = session.password_required;
    checked.value = true;
    if (session.authenticated && !wasAuthenticated) listeners.signedIn.forEach((callback) => callback());
    if (!session.authenticated && wasAuthenticated) listeners.signedOut.forEach((callback) => callback());
  }

  async function check() {
    try {
      apply(await authService.session());
    } catch (error) {
      apply({ authenticated: false, password_required: true });
    }
  }

  async function login(password) {
    apply(await authService.login(password));
  }

  async function logout() {
    apply(await authService.logout());
  }

  /** Called by the HTTP client when the API answers 401 (e.g. the session expired). */
  function sessionExpired() {
    if (authenticated.value) apply({ authenticated: false, password_required: true });
  }

  const on = (event, callback) => listeners[event].add(callback);

  return { checked, authenticated, passwordRequired, check, login, logout, sessionExpired, on };
}
