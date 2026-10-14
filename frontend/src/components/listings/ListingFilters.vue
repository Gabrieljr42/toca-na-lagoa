<!-- Sort bar and filter pills; emits a new filters object on every change. -->
<script setup>
import { computed } from 'vue';
import AppIcon from '../ui/AppIcon.vue';
import { useOptions } from '../../core/injection.js';
import {
  SELECT_FILTERS,
  TOGGLE_FILTERS,
  clearedFilters,
  countActiveFilters,
  defaultOrder,
} from '../../config/listingFilters.js';

const props = defineProps({
  neighborhoods: { type: Array, required: true },
});
const filters = defineModel({ type: Object, required: true });

const { options } = useOptions();
const selects = computed(() =>
  SELECT_FILTERS.map((filter) => ({
    ...filter,
    choices: filter.options({ neighborhoods: props.neighborhoods, options: options.value }),
  })),
);
const activeCount = computed(() => countActiveFilters(filters.value));

const update = (changes) => { filters.value = { ...filters.value, ...changes }; };
const setSort = (sort) => update({ sort, order: defaultOrder(sort) });
const flipOrder = () => update({ order: filters.value.order === 'asc' ? 'desc' : 'asc' });
const clear = () => { filters.value = clearedFilters(filters.value); };
</script>

<template>
  <div class="card mb-6 overflow-hidden">
    <div class="flex items-center gap-3 border-b border-slate-100 px-4 py-3 dark:border-slate-800">
      <span class="shrink-0 text-xs font-semibold uppercase tracking-wider text-slate-400">Ordenar</span>
      <div class="no-scrollbar -my-1 flex flex-1 gap-1.5 overflow-x-auto py-1" role="radiogroup" aria-label="Ordenar por">
        <button
          v-for="(label, key) in options.sort_labels"
          :key="key"
          type="button"
          role="radio"
          :aria-checked="filters.sort === key"
          class="chip shrink-0"
          :class="{ 'chip--solid': filters.sort === key }"
          @click="setSort(key)"
        >
          {{ label }}
        </button>
      </div>
      <button
        type="button"
        :title="filters.order === 'asc' ? 'Menor primeiro — clique para inverter' : 'Maior primeiro — clique para inverter'"
        class="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
        @click="flipOrder"
      >
        <AppIcon name="arrowDown" class="h-4 w-4 transition" :class="{ 'rotate-180': filters.order === 'desc' }" stroke-width="2" />
        <span class="hidden sm:inline">{{ filters.order === 'asc' ? 'Menor primeiro' : 'Maior primeiro' }}</span>
      </button>
    </div>

    <div class="flex flex-wrap items-center gap-2 px-4 py-3">
      <label v-for="select in selects" :key="select.key" class="pill-select" :class="{ 'pill-select--active': filters[select.key] }">
        <AppIcon :name="select.icon" class="h-4 w-4 shrink-0" />
        <select
          :aria-label="select.label"
          :value="filters[select.key]"
          class="cursor-pointer appearance-none border-0 bg-transparent py-0 pl-0 pr-5 text-sm font-medium focus:outline-none focus:ring-0"
          @change="update({ [select.key]: $event.target.value })"
        >
          <option value="">{{ select.label }}: todos</option>
          <option v-for="[value, label] in select.choices" :key="value" :value="value">{{ label }}</option>
        </select>
        <AppIcon name="chevronDown" class="pointer-events-none -ml-5 h-3.5 w-3.5 shrink-0 opacity-60" stroke-width="2.4" />
      </label>

      <span class="mx-1 hidden h-6 w-px bg-slate-200 sm:block dark:bg-slate-700" />

      <button
        v-for="toggle in TOGGLE_FILTERS"
        :key="toggle.key"
        type="button"
        :aria-pressed="filters[toggle.key]"
        class="chip gap-1.5"
        :class="{ 'chip--active': filters[toggle.key] }"
        @click="update({ [toggle.key]: !filters[toggle.key] })"
      >
        <AppIcon :name="toggle.icon" class="h-3.5 w-3.5" stroke-width="2" />
        {{ toggle.label }}
      </button>

      <button
        v-if="activeCount"
        type="button"
        class="ml-auto inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold text-slate-500 transition hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10"
        @click="clear"
      >
        <span class="grid h-4 min-w-4 place-items-center rounded-full bg-brand-600 px-1 text-[10px] text-white">{{ activeCount }}</span>
        Limpar
        <AppIcon name="close" class="h-3.5 w-3.5" stroke-width="2.4" />
      </button>
    </div>
  </div>
</template>
