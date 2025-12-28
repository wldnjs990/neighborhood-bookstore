<template>
  <div class="flex items-start gap-3">
    <div class="badge badge-primary badge-lg shrink-0 mt-1">✓</div>
    <p class="text-base">
      <span class="font-semibold">{{ props.title }}</span
      ><br />
      <span class="text-sm text-base-content/70">{{ props.content }}</span>
    </p>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  content: {
    type: String,
    required: true,
  },
})
</script>

<style lang="scss" scoped></style>
