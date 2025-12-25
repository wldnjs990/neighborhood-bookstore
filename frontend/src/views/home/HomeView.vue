<template>
  <div>홈</div>
  <BookCaracel :books="bestSellers" title="알라딘 베스트셀러" />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import BookCaracel from './components/BookCaracel.vue'
import { getBestSellerList } from '@/api/book'

const bestSellers = ref([])

onMounted(async () => {
  const bestSellersData = await getBestSellerList()
  console.log(bestSellersData)
  bestSellers.value = bestSellersData
})
</script>
