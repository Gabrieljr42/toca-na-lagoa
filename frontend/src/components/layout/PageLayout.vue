<!-- Page frame: gradient header with navigation and a hero slot, then the content. -->
<script setup>
import AppIcon from '../ui/AppIcon.vue';
import RouterLink from '../ui/RouterLink.vue';
import { useRouter } from '../../core/injection.js';
import { useTheme } from '../../stores/useTheme.js';

const { routes } = useRouter();
const { isDark, toggle: toggleTheme } = useTheme();
</script>

<template>
  <div class="min-h-full">
    <header class="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-teal-700 pb-28 text-white dark:from-slate-900 dark:via-slate-900 dark:to-teal-950">
      <div class="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/10 blur-2xl" />
      <div class="pointer-events-none absolute -bottom-32 left-10 h-72 w-72 rounded-full bg-teal-300/20 blur-3xl" />
      <nav class="relative mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-5 sm:px-6">
        <RouterLink to="/" class="flex items-center gap-3">
          <span class="grid h-10 w-10 place-items-center rounded-xl bg-white/15 ring-1 ring-white/25 backdrop-blur">
            <AppIcon name="home" class="h-6 w-6" />
          </span>
          <span>
            <span class="block whitespace-nowrap text-lg font-bold leading-tight">Toca na Lagoa</span>
            <span class="hidden text-xs text-white/70 sm:block">Aluguel para 1 pessoa · Pampulha, BH</span>
          </span>
        </RouterLink>
        <div class="flex items-center gap-1 rounded-xl bg-white/10 p-1 ring-1 ring-white/15 backdrop-blur">
          <RouterLink
            v-for="route in routes"
            :key="route.path"
            :to="route.path"
            class="whitespace-nowrap rounded-lg px-2.5 py-1.5 text-sm font-medium transition sm:px-3"
            active-class="bg-white text-brand-700 shadow dark:bg-white/90"
            inactive-class="text-white/80 hover:bg-white/10 hover:text-white"
          >
            {{ route.label }}
          </RouterLink>
          <button type="button" title="Alternar tema" class="ml-1 rounded-lg p-1.5 text-white/80 hover:bg-white/10 hover:text-white" @click="toggleTheme">
            <AppIcon :name="isDark ? 'sun' : 'moon'" class="h-5 w-5" />
          </button>
        </div>
      </nav>
      <div class="relative mx-auto max-w-6xl px-4 pt-6 sm:px-6">
        <slot name="hero" />
      </div>
    </header>
    <main class="relative mx-auto -mt-20 max-w-6xl px-4 pb-16 sm:px-6">
      <slot />
    </main>
  </div>
</template>
