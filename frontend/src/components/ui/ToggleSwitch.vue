<!-- On/off switch with a title and a description. -->
<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
});

const enabled = defineModel({ type: Boolean, required: true });
</script>

<template>
  <label class="flex cursor-pointer items-center justify-between gap-4 rounded-xl bg-slate-50 px-4 py-3 dark:bg-slate-800/60">
    <span>
      <span class="block text-sm font-semibold">{{ title }}</span>
      <span v-if="description" class="block text-xs text-slate-500">{{ description }}</span>
    </span>
    <input v-model="enabled" type="checkbox" class="peer sr-only">
    <span class="relative h-6 w-11 shrink-0 rounded-full bg-slate-300 transition after:absolute after:left-0.5 after:top-0.5 after:h-5 after:w-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:bg-brand-600 peer-checked:after:translate-x-5 peer-focus-visible:ring-2 peer-focus-visible:ring-brand-500 dark:bg-slate-600" />
  </label>
</template>
