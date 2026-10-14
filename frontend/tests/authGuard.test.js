import { ref } from 'vue';
import { describe, expect, it } from 'vitest';
import { createAuthGuard } from '../src/core/authGuard.js';

const guardFor = (state) => createAuthGuard({ checked: ref(state.checked ?? true), authenticated: ref(state.authenticated) });
const at = (path) => new URL(path, 'http://localhost');

describe('auth guard', () => {
  it('sends logged-out users to the login page remembering where they were going', () => {
    expect(guardFor({ authenticated: false })(at('/settings'))).toBe('/login?next=%2Fsettings');
  });

  it('sends logged-in users from the login page back to the remembered page', () => {
    expect(guardFor({ authenticated: true })(at('/login?next=%2F%3Ffavorites%3D1'))).toBe('/?favorites=1');
  });

  it('ignores a "next" pointing to another site', () => {
    expect(guardFor({ authenticated: true })(at('/login?next=%2F%2Fevil.example'))).toBe('/');
  });

  it('waits for the session check before redirecting', () => {
    expect(guardFor({ checked: false, authenticated: false })(at('/settings'))).toBeNull();
  });
});
