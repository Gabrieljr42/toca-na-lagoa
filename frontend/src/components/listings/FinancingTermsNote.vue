<!-- The mortgage terms behind the installments shown on the sale cards, with a shortcut to change them. -->
<script setup>
import { computed } from 'vue';
import AppIcon from '../ui/AppIcon.vue';
import RouterLink from '../ui/RouterLink.vue';
import { formatDecimal } from '../../core/format.js';

const props = defineProps({
  terms: { type: Object, required: true },
});

const summary = computed(() => {
  const { down_payment_percent: downPayment, yearly_rate_percent: rate, term_years: years, system_label: system } = props.terms;
  return `entrada de ${downPayment}% · juros de ${formatDecimal(rate)}% a.a. · ${years} anos · ${system}`;
});
</script>

<template>
  <div class="flex flex-col gap-2 rounded-2xl bg-white px-4 py-3 text-sm shadow-sm ring-1 ring-slate-200 sm:flex-row sm:items-center sm:justify-between dark:bg-slate-900 dark:ring-slate-800">
    <p class="flex items-start gap-2 text-slate-600 dark:text-slate-300">
      <AppIcon name="bank" class="mt-0.5 h-4 w-4 shrink-0 text-brand-600 dark:text-brand-400" />
      <span>
        Parcelas estimadas com <b>{{ summary }}</b>.
        <span class="text-slate-400">Sem seguros e taxas do banco.</span>
      </span>
    </p>
    <RouterLink to="/settings" class="shrink-0 text-xs font-semibold text-brand-600 hover:underline dark:text-brand-400">Alterar condições →</RouterLink>
  </div>
</template>
