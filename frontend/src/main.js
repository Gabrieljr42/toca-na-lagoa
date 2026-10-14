/**
 * Composition root: builds the HTTP client, services and stores once and
 * provides them to the component tree. Nothing else constructs dependencies.
 */

import { createApp, markRaw } from 'vue';
import './styles/main.css';
import App from './App.vue';
import { HttpClient } from './core/httpClient.js';
import { MONITOR, OPTIONS, ROUTER, SERVICES, TOASTS } from './core/injection.js';
import { ListingsService } from './services/listingsService.js';
import { MonitorService } from './services/monitorService.js';
import { OptionsService } from './services/optionsService.js';
import { SettingsService } from './services/settingsService.js';
import { TelegramService } from './services/telegramService.js';
import { createMonitorStore } from './stores/monitorStore.js';
import { createOptionsStore } from './stores/optionsStore.js';
import { createRouter } from './stores/router.js';
import { createToastStore } from './stores/toastStore.js';
import ListingsPage from './components/listings/ListingsPage.vue';
import SettingsPage from './components/settings/SettingsPage.vue';

const http = new HttpClient();
const services = {
  listings: new ListingsService(http),
  settings: new SettingsService(http),
  telegram: new TelegramService(http),
  monitor: new MonitorService(http),
  options: new OptionsService(http),
};

const toasts = createToastStore();
const router = createRouter([
  { path: '/', label: 'Apartamentos', component: markRaw(ListingsPage) },
  { path: '/settings', label: 'Configurações', component: markRaw(SettingsPage) },
]);
const monitor = createMonitorStore(services.monitor, toasts);
const options = createOptionsStore(services.options, toasts);

options.load();
monitor.startPolling();

createApp(App)
  .provide(SERVICES, services)
  .provide(TOASTS, toasts)
  .provide(ROUTER, router)
  .provide(MONITOR, monitor)
  .provide(OPTIONS, options)
  .mount('#app');
