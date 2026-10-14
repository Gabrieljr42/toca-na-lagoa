/** Light/dark theme, remembered per browser. */

import { ref } from 'vue';

const isDark = ref(document.documentElement.classList.contains('dark'));

export function useTheme() {
  function toggle() {
    isDark.value = document.documentElement.classList.toggle('dark');
    try {
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    } catch (error) {}
  }

  return { isDark, toggle };
}
