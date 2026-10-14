/** Short-lived notifications shown in the corner of the screen. */

import { reactive } from 'vue';

const DURATION_MS = { success: 5000, error: 9000 };

export function createToastStore() {
  const items = reactive([]);
  let nextId = 0;

  function dismiss(id) {
    const index = items.findIndex((item) => item.id === id);
    if (index !== -1) items.splice(index, 1);
  }

  function push(kind, text) {
    const id = nextId++;
    items.push({ id, kind, text });
    setTimeout(() => dismiss(id), DURATION_MS[kind]);
  }

  return {
    items,
    dismiss,
    success: (text) => push('success', text),
    error: (text) => push('error', text),
  };
}
