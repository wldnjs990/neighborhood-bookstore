<template>
  <main class="max-w-300 min-h-screen w-full mx-auto">
    <Navbar />
    <RouterView />
  </main>
</template>

<script setup>
import Navbar from './components/Navbar.vue'
</script>
