<!-- Settings page: loads the settings once and hands them to the two panels. -->
<script setup>
import { onMounted, ref } from 'vue';
import PageLayout from '../layout/PageLayout.vue';
import SearchSettingsForm from './SearchSettingsForm.vue';
import TelegramPanel from './TelegramPanel.vue';
import { useServices, useToasts } from '../../core/injection.js';

const { settings: settingsService } = useServices();
const toasts = useToasts();
const settings = ref(null);

onMounted(async () => {
  try {
    settings.value = await settingsService.get();
  } catch (error) {
    toasts.error(error.message);
  }
});

const replace = (next) => { settings.value = next; };
</script>

<template>
  <PageLayout>
    <template #hero>
      <p class="text-sm font-medium uppercase tracking-wider text-white/60">Configurações</p>
      <h1 class="mt-1 text-3xl font-extrabold tracking-tight sm:text-4xl">O que buscar e quando avisar</h1>
    </template>

    <div v-if="!settings" class="card p-10 text-center text-slate-500">Carregando…</div>
    <div v-else class="grid gap-6 lg:grid-cols-2">
      <SearchSettingsForm :settings="settings" @saved="replace" />
      <TelegramPanel :settings="settings" @saved="replace" />
    </div>
  </PageLayout>
</template>
