<!-- Editable list of "HH:MM" check times. -->
<script setup>
import AppIcon from '../ui/AppIcon.vue';

const NEW_TIME = '12:00';

const times = defineModel({ type: Array, required: true });

const change = (index, value) => { times.value = times.value.map((time, position) => (position === index ? value : time)); };
const remove = (index) => { times.value = times.value.filter((_, position) => position !== index); };
const add = () => { times.value = [...times.value, NEW_TIME]; };
</script>

<template>
  <div>
    <span class="label">Horários de verificação</span>
    <div class="flex flex-wrap items-center gap-2">
      <div
        v-for="(time, index) in times"
        :key="index"
        class="flex items-center gap-1 rounded-xl bg-slate-50 py-1 pl-1 pr-2 ring-1 ring-slate-200 dark:bg-slate-800 dark:ring-slate-700"
      >
        <input
          type="time"
          :value="time"
          required
          aria-label="Horário"
          class="rounded-lg border-0 bg-transparent px-2 py-1 text-sm focus:ring-2 focus:ring-brand-500"
          @change="change(index, $event.target.value)"
        >
        <button v-if="times.length > 1" type="button" class="text-slate-400 hover:text-rose-500" title="Remover" @click="remove(index)">
          <AppIcon name="close" class="h-3.5 w-3.5" stroke-width="2.4" />
        </button>
      </div>
      <button type="button" class="rounded-xl px-3 py-2 text-sm font-semibold text-brand-600 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-500/10" @click="add">
        + horário
      </button>
    </div>
  </div>
</template>
