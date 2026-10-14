<!-- Root component: renders the current page and the toast stack. -->
<script setup>
import ToastStack from './components/ui/ToastStack.vue';
import { useRouter } from './core/injection.js';

const { current } = useRouter();
</script>

<template>
  <component :is="current.component" :key="current.path" />
  <ToastStack />
</template>
