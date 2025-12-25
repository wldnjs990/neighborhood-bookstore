<template>
  <main class="bg-base-100 min-h-screen">
    <!-- 로딩 중 -->
    <div v-if="loading" class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="flex justify-center items-center py-20">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    </div>

    <!-- 거래 상세 정보 -->
    <div v-else-if="trade && trade.id" class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- 상단: 제목, 가격, 상태 -->
      <TradeDetailHeader :trade="trade" />

      <!-- 중간: 이미지 & 상세 정보 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 pb-8 mb-8 border-b border-base-content/10">
        <!-- 왼쪽: 거래 이미지 -->
        <TradeDetailImage :image="trade.image" :alt="trade.title" />

        <!-- 오른쪽: 도서 정보 및 설명 -->
        <TradeDetailInfo :book="trade.book" :content="trade.content" />
      </div>
      <!-- 거래 도서 카드 -->
      <TradeBookCard :book="trade.book" />

      <!-- 하단: 액션 버튼 -->
      <div class="flex justify-center mt-5">
        <div class="w-full max-w-md">
          <TradeDetailActions
            :trade-id="trade.id"
            :is-owner="isOwner"
            :kakao-chat-url="trade.kakaoChatUrl || trade.kakao_chat_url"
            @delete="handleDelete"
          />
        </div>
      </div>
    </div>

    <!-- 거래를 찾을 수 없음 -->
    <div v-else class="container mx-auto px-4 py-8 max-w-6xl">
      <div class="flex flex-col items-center justify-center py-20 text-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-24 w-24 text-base-content/20 mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 class="text-2xl font-bold text-base-content/50 mb-2">거래를 찾을 수 없습니다</h3>
        <p class="text-base-content/40 mb-6">삭제되었거나 존재하지 않는 거래입니다</p>
        <RouterLink :to="{ name: 'trade' }" class="btn btn-primary"> 목록으로 돌아가기 </RouterLink>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useLoginStore } from '@/stores/loginStore'
import { useToastStore } from '@/stores/toastStore'
import { getTradeDetail, deleteTrade as deleteTradeApi } from '@/api/trades'
import TradeDetailHeader from './components/TradeDetailHeader.vue'
import TradeDetailImage from './components/TradeDetailImage.vue'
import TradeDetailInfo from './components/TradeDetailInfo.vue'
import TradeDetailActions from './components/TradeDetailActions.vue'
import TradeBookCard from './components/TradeBookCard.vue'

// ==================== 라우터 ====================
const route = useRoute()
const router = useRouter()
const loginStore = useLoginStore()
const toastStore = useToastStore()

// ==================== 상태 관리 ====================
const trade = ref(null)
const loading = ref(true)

// ==================== Computed ====================
// 본인 게시글 여부 확인
const isOwner = computed(() => {
  if (!trade.value || !loginStore.user) return false
  return trade.value.user?.id === loginStore.user.id
})

// ==================== Methods ====================
// 거래 상세 정보 가져오기
const fetchTradeDetail = async () => {
  loading.value = true
  try {
    const { id } = route.params
    const response = await getTradeDetail(id)
    trade.value = response.data
  } catch (error) {
    console.error('거래 상세 조회 실패:', error)
    trade.value = null
  } finally {
    loading.value = false
  }
}

// 거래 삭제
const handleDelete = async () => {
  try {
    await deleteTradeApi(trade.value.id)
    toastStore.showToast('거래가 삭제되었습니다.', 'success')
    router.push({ name: 'trade' })
  } catch (error) {
    console.error('거래 삭제 실패:', error)
    toastStore.showToast('거래 삭제에 실패했습니다.', 'error')
  }
}

// ==================== Lifecycle ====================
onMounted(() => {
  fetchTradeDetail()
})
</script>
