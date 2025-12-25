<template>
  <div v-if="toastStore.show" class="toast toast-center toast-bottom z-50">
    <div class="alert" :class="toastStore.type === 'success' ? 'alert-success' : 'alert-error'">
      <span>{{ toastStore.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toastStore'

const toastStore = useToastStore()
</script>
