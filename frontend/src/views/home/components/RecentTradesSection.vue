<template>
  <!-- ==================== 최신 중고거래 섹션 ==================== -->
  <section class="py-16 bg-base-200/30">
    <div class="flex flex-col items-center pb-10">
      <h2 class="text-3xl font-bold mb-2">🛒 최신 중고거래</h2>
      <p class="text-base-content/70">방금 올라온 따끈따끈한 중고 도서들을 확인해보세요!</p>
    </div>
    <div class="container mx-auto px-4">
      <!-- 로딩 상태 -->
      <div
        v-if="loading"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
      >
        <TradeCardSkeleton v-for="i in 5" :key="i" />
      </div>

      <!-- 거래 목록 -->
      <div
        v-else-if="trades.length > 0"
        class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
      >
        <TradeCard v-for="trade in trades" :key="trade.id" :trade="trade" />
      </div>

      <!-- 거래 없을 때 -->
      <div v-else class="flex flex-col items-center justify-center py-20 text-center">
        <ShoppingBagIcon class="h-24 w-24 text-base-content/20 mb-4" />
        <h3 class="text-2xl font-bold text-base-content/50 mb-2">등록된 거래가 없습니다</h3>
        <p class="text-base-content/40">첫 번째 거래를 등록해보세요!</p>
      </div>

      <!-- 전체 보기 버튼 -->
      <div class="flex justify-center">
        <RouterLink :to="{ name: 'trade' }" class="btn btn-outline btn-primary">
          전체 보기
          <ChevronRightIcon class="h-5 w-5 ml-1" />
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import TradeCard from '@/components/TradeCard.vue'
import TradeCardSkeleton from '@/views/trade/components/TradeCardSkeleton.vue'
import { searchTrades } from '@/api/trades'
import { ChevronRightIcon, ShoppingBagIcon } from '@heroicons/vue/24/outline'

const trades = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 최신순으로 5개 가져오기
    const response = await searchTrades({
      page: 1,
      size: 10,
    })
    trades.value = response.data.results.slice(0, 10)
  } catch (error) {
    console.error('최신 거래 로드 실패:', error)
  } finally {
    loading.value = false
  }
})
</script>
