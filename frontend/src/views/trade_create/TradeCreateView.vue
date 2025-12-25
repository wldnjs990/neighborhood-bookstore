<template>
  <main class="bg-base-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
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
          <h1 class="text-3xl font-bold">중고거래 등록</h1>
        </div>
        <p class="text-base-content/60 pl-14">읽지 않는 책을 다른 사람과 나눠보세요</p>
      </div>

      <!-- 등록 폼 -->
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- 1. 도서 검색 -->
        <BookSearchInput
          v-model="selectedBook"
          v-model:search-results="bookResults"
          @search="searchBooks"
        />

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
        <TradeFormImage v-model="form.image" :preview="imagePreview" />

        <!-- 제출 버튼 -->
        <div class="card bg-base-100 shadow-sm border border-base-content/5">
          <div class="card-body p-6">
            <div class="flex gap-3">
              <button
                type="submit"
                class="btn btn-primary flex-1"
                :disabled="!selectedBook || !form.title || !form.content"
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
                등록하기
              </button>
              <button type="button" @click="handleCancel" class="btn btn-outline">취소</button>
            </div>
            <p
              v-if="!selectedBook || !form.title || !form.content"
              class="text-xs text-warning text-center mt-2"
            >
              필수 항목을 모두 입력해주세요
            </p>
          </div>
        </div>
      </form>
    </div>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { createTrade } from '@/api/trades'
import client from '@/api/client'
import { useToastStore } from '@/stores/toastStore'
import BookSearchInput from './components/BookSearchInput.vue'
import TradeFormBasicInfo from './components/TradeFormBasicInfo.vue'
import TradeFormPriceRegion from './components/TradeFormPriceRegion.vue'
import TradeFormImage from './components/TradeFormImage.vue'

// ==================== 라우터 ====================
const router = useRouter()
const toastStore = useToastStore()

// ==================== 상태 관리 ====================
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

// 도서 검색 관련
const bookResults = ref([])
const selectedBook = ref(null)

// 이미지 미리보기
const imagePreview = ref(null)

// ==================== Methods ====================
// 도서 검색 (자동완성)
let searchTimeout = null
const searchBooks = (query) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    if (query.length < 1) {
      bookResults.value = []
      return
    }
    try {
      const response = await client.get('/api/books/autocomplete/', {
        params: { q: query },
      })
      bookResults.value = response.data
    } catch (error) {
      console.error('도서 검색 실패:', error)
      bookResults.value = []
    }
  }, 300)
}

// 취소 확인
const handleCancel = () => {
  if (form.title || form.content || selectedBook.value) {
    // DaisyUI 모달로 확인받기 (구현 복잡도를 고려하여 일단 직접 뒤로가기)
    router.back()
  } else {
    router.back()
  }
}

// 폼 제출
const handleSubmit = async () => {
  // 필수 항목 검증
  if (!selectedBook.value) {
    toastStore.showToast('도서를 선택해주세요.', 'error')
    return
  }
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
    if (form.image) {
      formData.append('image', form.image)
    }

    // API 호출
    await createTrade(selectedBook.value.id, formData)
    toastStore.showToast('게시글이 등록되었습니다.', 'success')
    router.push({ name: 'trade' })
  } catch (error) {
    console.error('게시글 등록 실패:', error)

    // 에러 메시지 처리
    if (error.response?.data) {
      const errors = error.response.data
      const message = Object.values(errors).flat().join(', ')
      toastStore.showToast(`등록 실패: ${message}`, 'error')
    } else {
      toastStore.showToast('게시글 등록에 실패했습니다. 다시 시도해주세요.', 'error')
    }
  }
}
</script>
