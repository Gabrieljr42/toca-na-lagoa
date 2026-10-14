<!-- Link that navigates inside the app without reloading the page. -->
<script setup>
import { computed } from 'vue';
import { useRouter } from '../../core/injection.js';

const props = defineProps({
  to: { type: String, required: true },
  activeClass: { type: String, default: '' },
  inactiveClass: { type: String, default: '' },
});

const router = useRouter();
const isActive = computed(() => router.path.value === props.to);

function navigate(event) {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.button !== 0) return;
  event.preventDefault();
  router.push(props.to);
}
</script>

<template>
  <a :href="to" :class="isActive ? activeClass : inactiveClass" :aria-current="isActive ? 'page' : null" @click="navigate">
    <slot />
  </a>
</template>
