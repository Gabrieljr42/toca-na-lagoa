<!-- The filters currently applied, each removable with one tap. -->
<script setup>
import AppIcon from '../ui/AppIcon.vue';

defineProps({
  items: { type: Array, required: true },
});
defineEmits(['remove']);
</script>

<template>
  <div v-if="items.length" class="no-scrollbar flex gap-1.5 overflow-x-auto">
    <button
      v-for="item in items"
      :key="item.key"
      type="button"
      :title="`Remover filtro ${item.label}`"
      class="chip chip--active shrink-0 gap-1"
      @click="$emit('remove', item.key)"
    >
      {{ item.label }}
      <AppIcon name="close" class="h-3 w-3" stroke-width="2.6" />
    </button>
  </div>
</template>
