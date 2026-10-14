/**
 * Dependency injection keys. The composition root (main.js) provides every
 * service and store; components ask for what they need through these helpers
 * and never construct dependencies themselves.
 */

import { inject } from 'vue';

export const SERVICES = Symbol('services');
export const ROUTER = Symbol('router');
export const TOASTS = Symbol('toasts');
export const MONITOR = Symbol('monitor');
export const OPTIONS = Symbol('options');

function required(key, name) {
  const value = inject(key, null);
  if (value === null) {
    throw new Error(`${name} was not provided by the app`);
  }
  return value;
}

export const useServices = () => required(SERVICES, 'services');
export const useRouter = () => required(ROUTER, 'router');
export const useToasts = () => required(TOASTS, 'toasts');
export const useMonitor = () => required(MONITOR, 'monitor');
export const useOptions = () => required(OPTIONS, 'options');
