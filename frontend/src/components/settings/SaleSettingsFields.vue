<!--
  Criteria for apartments to buy and the mortgage terms used to estimate their
  installments. Edits the parent form's draft in place.
-->
<script setup>
import ToggleSwitch from '../ui/ToggleSwitch.vue';
import PriceRangeInput from './PriceRangeInput.vue';

defineProps({
  systemLabels: { type: Object, required: true },
});
const draft = defineModel({ type: Object, required: true });
</script>

<template>
  <div class="space-y-5">
    <ToggleSwitch
      v-model="draft.sale_enabled"
      title="Buscar apartamentos à venda"
      description="Faz uma segunda busca em cada verificação, com os critérios abaixo, e mostra o resultado na aba Comprar."
    />

    <template v-if="draft.sale_enabled">
      <div class="grid gap-4 sm:grid-cols-2">
        <label class="block">
          <span class="label">Máximo de quartos</span>
          <input v-model.number="draft.sale_max_bedrooms" type="number" min="0" max="5" class="field">
        </label>
        <label class="block">
          <span class="label">Área máxima (m², vazio = sem limite)</span>
          <input v-model="draft.sale_max_area" inputmode="numeric" class="field">
        </label>
      </div>

      <PriceRangeInput
        v-model:min="draft.sale_min_price"
        v-model:max="draft.sale_max_price"
        legend="Preço do imóvel (R$, vazio = sem limite)"
        min-placeholder="ex.: 250.000"
        max-placeholder="ex.: 450.000"
      />

      <fieldset class="rounded-xl bg-slate-50 p-4 dark:bg-slate-800/60">
        <legend class="sr-only">Financiamento</legend>
        <p class="mb-3 text-sm font-semibold">Financiamento</p>
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <label class="block">
            <span class="label">Entrada (%)</span>
            <input v-model.number="draft.financing_down_payment_percent" type="number" min="0" max="100" class="field">
          </label>
          <label class="block">
            <span class="label">Juros (% a.a.)</span>
            <input v-model="draft.financing_rate" inputmode="decimal" placeholder="ex.: 11,5" class="field">
          </label>
          <label class="block">
            <span class="label">Prazo (anos)</span>
            <input v-model.number="draft.financing_term_years" type="number" min="1" max="35" class="field">
          </label>
          <label class="block">
            <span class="label">Sistema</span>
            <select v-model="draft.financing_system" class="field cursor-pointer">
              <option v-for="(label, value) in systemLabels" :key="value" :value="value">{{ label }}</option>
            </select>
          </label>
        </div>
        <label class="mt-4 block">
          <span class="label">Custo mensal máximo (1ª parcela + cond. + IPTU, vazio = sem limite)</span>
          <input v-model="draft.sale_max_monthly" inputmode="numeric" placeholder="ex.: 3.500" class="field">
        </label>
        <p class="mt-3 text-xs leading-relaxed text-slate-500">
          No <b>SAC</b> a parcela começa mais alta e cai todo mês; na <b>Price</b> ela é fixa.
          A estimativa usa a taxa efetiva anual e não inclui seguros (MIP/DFI) nem taxas do banco.
        </p>
      </fieldset>
    </template>
  </div>
</template>
