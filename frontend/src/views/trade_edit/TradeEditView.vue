<template>
  <main class="bg-base-100 min-h-screen">
    <!-- 로딩 중 -->
    <div v-if="loading" class="container mx-auto px-4 py-8 max-w-4xl">
      <div class="flex justify-center items-center py-20">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
    </div>

    <!-- 수정 폼 -->
    <div v-else-if="trade" class="container mx-auto px-4 py-8 max-w-4xl">
      <!-- 헤더 -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-3">
          <button type="button" @click="router.back()" class="btn btn-ghost btn-circle btn-sm">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
          </button>
          <h1 class="text-3xl font-bold">중고거래 수정</h1>
        </div>
        <p class="text-base-content/60 pl-14">거래 정보를 수정하세요</p>
      </div>

      <!-- 수정 폼 -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- 1. 도서 정보 (수정 불가, 읽기 전용) -->
        <div class="card bg-base-100 shadow-sm border border-base-content/5">
          <div class="card-body p-6">
            <h3 class="text-lg font-bold mb-4">도서 정보</h3>
            <div class="flex gap-4 items-center">
              <img
                :src="trade.book.cover"
                :alt="trade.book.title"
                class="w-16 h-20 object-cover rounded"
              />
              <div>
                <p class="font-bold">{{ trade.book.title }}</p>
                <p class="text-sm text-base-content/60">{{ trade.book.author }}</p>
              </div>
            </div>
            <p class="text-xs text-base-content/50 mt-2">도서는 변경할 수 없습니다</p>
          </div>
        </div>

        <!-- 2. 기본 정보 -->
        <TradeFormBasicInfo v-model:title="form.title" v-model:content="form.content" />

        <!-- 3. 가격 및 거래 정보 -->
        <TradeFormPriceRegion
          v-model:sale-type="form.saleType"
          v-model:price="form.price"
          v-model:region="form.region"
          v-model:kakao-chat-url="form.kakaoChatUrl"
        />

        <!-- 4. 이미지 업로드 -->
        <TradeFormImage v-model="form.image" :preview="imagePreview" :existing-image="trade.image" />

        <!-- 제출 버튼 -->
        <div class="card bg-base-100 shadow-sm border border-base-content/5">
          <div class="card-body p-6">
            <div class="flex gap-3">
              <button
                type="submit"
                class="btn btn-primary flex-1"
                :disabled="!form.title || !form.content"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                수정하기
              </button>
              <button type="button" @click="router.back()" class="btn btn-outline">취소</button>
            </div>
            <p v-if="!form.title || !form.content" class="text-xs text-warning text-center mt-2">
              필수 항목을 모두 입력해주세요
            </p>
          </div>
        </div>
      </form>
    </div>

    <!-- 거래를 찾을 수 없음 -->
    <div v-else class="container mx-auto px-4 py-8 max-w-4xl">
      <div class="flex flex-col items-center justify-center py-20 text-center">
        <h3 class="text-2xl font-bold text-base-content/50 mb-2">거래를 찾을 수 없습니다</h3>
        <p class="text-base-content/40 mb-6">삭제되었거나 존재하지 않는 거래입니다</p>
        <button @click="router.push({ name: 'trade' })" class="btn btn-primary">
          목록으로 돌아가기
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToastStore } from '@/stores/toastStore'
import { getTradeDetail, updateTrade } from '@/api/trades'
import TradeFormBasicInfo from '../trade_create/components/TradeFormBasicInfo.vue'
import TradeFormPriceRegion from '../trade_create/components/TradeFormPriceRegion.vue'
import TradeFormImage from '../trade_create/components/TradeFormImage.vue'

// ==================== 라우터 ====================
const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()

// ==================== 상태 관리 ====================
const trade = ref(null)
const loading = ref(true)

// 폼 데이터
const form = reactive({
  title: '',
  content: '',
  saleType: 'sale',
  price: 0,
  region: 'seoul',
  kakaoChatUrl: '',
  image: null,
})

// 이미지 미리보기
const imagePreview = ref(null)

// ==================== Methods ====================
// 거래 상세 정보 가져오기
const fetchTradeDetail = async () => {
  loading.value = true
  try {
    const { id } = route.params
    const response = await getTradeDetail(id)
    trade.value = response.data

    // 폼 데이터 초기화
    form.title = trade.value.title
    form.content = trade.value.content
    form.saleType = trade.value.saleType || trade.value.sale_type || 'sale'
    form.price = trade.value.price || 0
    form.region = trade.value.region || 'seoul'
    form.kakaoChatUrl = trade.value.kakaoChatUrl || trade.value.kakao_chat_url || ''

    // 기존 이미지 미리보기
    if (trade.value.image) {
      imagePreview.value = trade.value.image
    }
  } catch (error) {
    console.error('거래 조회 실패:', error)
    trade.value = null
    toastStore.showToast('거래를 불러오는데 실패했습니다.', 'error')
  } finally {
    loading.value = false
  }
}

// 폼 제출
const handleSubmit = async () => {
  // 필수 항목 검증
  if (!form.title.trim()) {
    toastStore.showToast('제목을 입력해주세요.', 'error')
    return
  }
  if (!form.content.trim()) {
    toastStore.showToast('상세 설명을 입력해주세요.', 'error')
    return
  }

  try {
    // FormData 생성
    const formData = new FormData()
    formData.append('title', form.title.trim())
    formData.append('content', form.content.trim())
    formData.append('saleType', form.saleType)
    formData.append('price', form.saleType === 'free' ? 0 : form.price)
    formData.append('region', form.region)

    // 선택 항목
    if (form.kakaoChatUrl && form.kakaoChatUrl.trim()) {
      formData.append('kakaoChatUrl', form.kakaoChatUrl.trim())
    }
    // 새로운 이미지가 업로드된 경우에만 추가
    if (form.image) {
      formData.append('image', form.image)
    }

    // API 호출
    await updateTrade(trade.value.id, formData)
    toastStore.showToast('게시글이 수정되었습니다.', 'success')
    router.push({ name: 'tradeDetail', params: { id: trade.value.id } })
  } catch (error) {
    console.error('게시글 수정 실패:', error)

    // 에러 메시지 처리
    if (error.response?.data) {
      const errors = error.response.data
      const message = Object.values(errors).flat().join(', ')
      toastStore.showToast(`수정 실패: ${message}`, 'error')
    } else {
      toastStore.showToast('게시글 수정에 실패했습니다. 다시 시도해주세요.', 'error')
    }
  }
}

// ==================== Lifecycle ====================
onMounted(() => {
  fetchTradeDetail()
})
</script>
