<!-- Inline SVG icon from the shared icon set. -->
<script setup>
import { computed } from 'vue';
import { ICONS } from '../../config/icons.js';

const props = defineProps({
  name: { type: String, required: true },
  filled: { type: Boolean, default: false },
  strokeWidth: { type: [Number, String], default: 1.8 },
});

const paths = computed(() => ICONS[props.name] ?? '');
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    :fill="filled ? 'currentColor' : 'none'"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    v-html="paths"
  />
</template>
