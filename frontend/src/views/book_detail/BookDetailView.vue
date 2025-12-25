<template>
  <main class="bg-base-100 min-h-screen">
    <div v-if="book.id" class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- 상단: 제목, 저자, 출판사, 카테고리, 북마크 -->
      <div class="pb-6 mb-8 border-b border-base-content/10">
        <div class="flex justify-between items-start gap-4">
          <!-- 왼쪽: 도서 기본 정보 -->
          <div class="flex-1">
            <h1 class="text-3xl font-bold text-base-content mb-4">{{ book.title }}</h1>
            <div class="flex flex-wrap gap-2 text-base-content/70 text-lg">
              <span>{{ book.author }}</span>
              <span>·</span>
              <span>{{ book.publisher }}</span>
              <span>·</span>
              <span>{{ book.pubDate }}</span>
            </div>
            <div class="mt-4">
              <span class="badge badge-primary badge-md">{{ book.category?.name }}</span>
            </div>
          </div>

          <!-- 오른쪽: 북마크 & 평점 버튼 -->
          <div class="flex gap-2">
            <!-- 평점 주기 버튼 -->
            <button
              @click="openRatingModal"
              class="btn btn-circle btn-lg btn-ghost"
              title="평점 주기"
            >
              <StarIconSolid v-if="userRating" class="w-8 h-8 text-warning" />
              <StarIcon v-else class="w-8 h-8" />
            </button>

            <!-- 북마크 버튼 -->
            <button
              @click="handleBookmark(book.id)"
              class="btn btn-circle btn-lg"
              :class="book.isBookmarked ? 'btn-error' : 'btn-ghost'"
              title="북마크"
            >
              <BookmarkIconSolid v-if="book.isBookmarked" class="w-8 h-8" />
              <BookmarkIcon v-else class="w-8 h-8" />
            </button>
          </div>
        </div>
      </div>

      <!-- 평점 모달 -->
      <dialog ref="ratingModal" class="modal">
        <div class="modal-box">
          <h3 class="text-2xl font-bold mb-4">이 책의 평점을 남겨주세요</h3>

          <!-- 별점 선택 -->
          <div class="flex flex-col items-center gap-6 py-6">
            <div class="flex gap-2">
              <button
                v-for="star in 5"
                :key="star"
                @click="selectedRating = star"
                class="btn btn-ghost btn-lg p-2"
              >
                <StarIconSolid
                  v-if="star <= (hoverRating || selectedRating)"
                  @mouseenter="hoverRating = star"
                  @mouseleave="hoverRating = 0"
                  class="w-12 h-12 text-warning"
                />
                <StarIcon
                  v-else
                  @mouseenter="hoverRating = star"
                  @mouseleave="hoverRating = 0"
                  class="w-12 h-12"
                />
              </button>
            </div>

            <div class="text-center">
              <p class="text-3xl font-bold text-primary">{{ selectedRating }}.0</p>
              <p class="text-sm text-base-content/60 mt-1">{{ getRatingText(selectedRating) }}</p>
            </div>
          </div>

          <!-- 버튼 -->
          <div class="modal-action">
            <form method="dialog" class="flex gap-2">
              <button class="btn btn-ghost">취소</button>
              <button
                @click="handleRating"
                :disabled="selectedRating === 0"
                class="btn btn-primary"
              >
                평점 등록
              </button>
            </form>
          </div>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button>close</button>
        </form>
      </dialog>

      <!-- 중간: 도서 이미지 & 상세 정보 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 pb-8 mb-8 border-b border-base-content/10">
        <!-- 왼쪽: 도서 이미지 -->
        <figure class="flex justify-center items-start">
          <ThreeDimentionImage :images="[{ src: book.cover, alt: `${book.title} 커버 이미지` }]" />
        </figure>

        <!-- 오른쪽: 상세 정보 -->
        <div class="flex flex-col gap-8">
          <!-- 평점 & 순위 정보 -->
          <div class="space-y-4">
            <h3 class="text-xl font-bold border-b border-base-content/10 pb-2">평가 및 순위</h3>
            <div class="grid grid-cols-1 gap-4">
              <div class="flex justify-between items-center py-3 border-b border-base-content/5">
                <span class="text-base-content/70">알라딘 평점</span>
                <span class="text-2xl font-bold"
                  >{{ book.customerReviewRank
                  }}<span class="text-sm text-base-content/50">/10</span></span
                >
              </div>
              <div class="flex justify-between items-center py-3 border-b border-base-content/5">
                <span class="text-base-content/70">알라딘 베스트셀러 순위</span>
                <span class="text-2xl font-bold"
                  >{{ book.bestRank || '-'
                  }}<span class="text-sm text-base-content/50">위</span></span
                >
              </div>
              <div class="flex justify-between items-center py-3">
                <span class="text-base-content/70">동네책방 사용자 평가</span>
                <div class="text-right">
                  <div class="text-2xl font-bold">
                    {{ Number(book.averageRating || 0).toFixed(2) }}
                  </div>
                  <div class="text-sm text-base-content/50">{{ book.ratingCount }}개의 평가</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 가격 정보 -->
          <div class="space-y-4">
            <div class="flex items-center gap-2 border-b border-base-content/10 pb-2">
              <h3 class="text-xl font-bold flex-1">알라딘 가격 정보</h3>
              <a
                :href="`https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=${book.itemId}`"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-ghost btn-sm btn-circle"
                title="알라딘 도서 페이지로 이동"
              >
                <ArrowTopRightOnSquareIcon class="w-5 h-5" />
              </a>
            </div>
            <div class="flex items-center justify-between py-3">
              <div class="flex flex-col gap-2">
                <span class="text-sm text-base-content/60 line-through">
                  정가: {{ book.priceStandard?.toLocaleString() }}원
                </span>
                <span class="text-3xl font-bold text-error">
                  {{ book.priceSales?.toLocaleString() }}원
                </span>
              </div>
              <div class="badge badge-error badge-lg h-12 text-lg">
                {{
                  Math.round(((book.priceStandard - book.priceSales) / book.priceStandard) * 100)
                }}% 할인
              </div>
            </div>
          </div>

          <!-- 도서 설명 -->
          <div class="space-y-3">
            <h3 class="text-xl font-bold border-b border-base-content/10 pb-2">도서 소개</h3>
            <p v-if="book.description" class="text-base-content/80 leading-relaxed">
              {{ book.description }}
            </p>
            <p v-else class="text-base-content/60 italic">도서 소개가 제공되지 않습니다.</p>
          </div>
        </div>
      </div>

      <!-- 하단 섹션: 중고 거래 정보 -->
      <div class="pt-4">
        <div class="flex items-center justify-between mb-6 border-b border-base-content/10 pb-3">
          <h2 class="text-2xl font-bold">동네책방 중고 거래</h2>
          <span v-if="book.trades && book.trades.length > 0" class="badge badge-primary badge-lg">
            {{ book.trades.length }}건
          </span>
        </div>

        <!-- 중고 거래 목록 그리드 -->
        <div
          v-if="book.trades && book.trades.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
          <TradeCard v-for="trade in book.trades" :key="trade.id" :trade="trade" />
        </div>

        <!-- 중고 거래 없을 때 -->
        <div v-else class="alert alert-info">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            class="stroke-current shrink-0 w-6 h-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <span>현재 등록된 중고 거래가 없습니다.</span>
        </div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-else class="flex justify-center items-center min-h-screen">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  </main>
</template>

<script setup>
import { getBookDetail, toggleBookmark, rateBook } from '@/api/book'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BookmarkIcon, ArrowTopRightOnSquareIcon, StarIcon } from '@heroicons/vue/24/outline'
import {
  BookmarkIcon as BookmarkIconSolid,
  StarIcon as StarIconSolid,
} from '@heroicons/vue/24/solid'
import ThreeDimentionImage from '@/components/ThreeDimentionImage.vue'
import TradeCard from '@/components/TradeCard.vue'
import { useToastStore } from '@/stores/toastStore'
import { useLoginStore } from '@/stores/loginStore'

const route = useRoute()
const router = useRouter()
const toastStore = useToastStore()
const loginStore = useLoginStore()

const book = ref({})
const ratingModal = ref(null)
const selectedRating = ref(0)
const hoverRating = ref(0)
const userRating = ref(null) // 사용자가 이미 준 평점

onMounted(async () => {
  const data = await getBookDetail(route.params.id)
  console.log(data)
  book.value = data
  // 사용자가 이미 준 평점이 있다면 userRating에 설정
  userRating.value = data.userRating
})

const handleBookmark = async (id) => {
  // 인증 확인
  if (!loginStore.token) {
    router.push({ name: 'login', query: { redirect: route.fullPath, authRequired: 'true' } })
    return
  }

  const response = await toggleBookmark(id)
  console.log(response.message)
  book.value.isBookmarked = response.isBookmarked

  // 토스트 메시지
  if (response.isBookmarked) {
    toastStore.showToast('북마크에 추가되었습니다!', 'success')
  } else {
    toastStore.showToast('북마크가 해제되었습니다.', 'success')
  }
}

const openRatingModal = () => {
  // 인증 확인
  if (!loginStore.token) {
    router.push({ name: 'login', query: { redirect: route.fullPath, authRequired: 'true' } })
    return
  }

  selectedRating.value = userRating.value || 0
  ratingModal.value.showModal()
}

const handleRating = async () => {
  if (selectedRating.value === 0) return

  try {
    const response = await rateBook(book.value.id, selectedRating.value)
    console.log(response.message)

    // 평점 정보 업데이트
    userRating.value = selectedRating.value
    book.value.averageRating = Number(response.averageRating).toFixed(2)
    book.value.ratingCount = response.ratingCount

    // 모달 닫기
    ratingModal.value.close()

    // 성공 메시지
    toastStore.showToast('평점이 등록되었습니다!', 'success')
  } catch (error) {
    console.error('평점 등록 실패:', error)
    toastStore.showToast('평점 등록에 실패했습니다. 다시 시도해주세요.', 'error')
  }
}

const getRatingText = (rating) => {
  const texts = {
    0: '별점을 선택해주세요',
    1: '별로예요',
    2: '그저 그래요',
    3: '괜찮아요',
    4: '좋아요',
    5: '최고예요!',
  }
  return texts[rating] || ''
}
</script>
