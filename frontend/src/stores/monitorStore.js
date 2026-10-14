/**
 * Monitor status shared by every page. Polls the API so the UI refreshes on its
 * own when a scheduled check finishes, and notifies subscribers (e.g. the
 * listings page reloads its cards).
 */

import { computed, ref } from 'vue';
import { formatDateTime } from '../core/format.js';

const POLL_INTERVAL_MS = 30000;

export function createMonitorStore(monitorService, toasts) {
  const status = ref(null);
  const checking = ref(false);
  const subscribers = new Set();

  const busy = computed(() => checking.value || Boolean(status.value?.running));

  function onCheckFinished(callback) {
    subscribers.add(callback);
    return () => subscribers.delete(callback);
  }

  function notify() {
    subscribers.forEach((callback) => callback(status.value));
  }

  async function refresh() {
    if (checking.value) return;
    const previous = status.value;
    status.value = await monitorService.status();
    if (previous && status.value.last_check_at !== previous.last_check_at) {
      toasts.success(`Lista atualizada pela verificação de ${formatDateTime(status.value.last_check_at)}`);
      notify();
    }
  }

  async function checkNow() {
    checking.value = true;
    try {
      status.value = await monitorService.checkNow();
      toasts.success('Verificação concluída');
      notify();
    } catch (error) {
      toasts.error(error.message);
    } finally {
      checking.value = false;
    }
  }

  function startPolling() {
    const poll = () => {
      if (!document.hidden) refresh().catch(() => {});
    };
    poll();
    setInterval(poll, POLL_INTERVAL_MS);
    document.addEventListener('visibilitychange', poll);
  }

  return { status, busy, checkNow, refresh, onCheckFinished, startPolling };
}
