<template>
  <!-- ==================== 도서 카드 ==================== -->
  <RouterLink
    :to="{ name: 'bookDetail', params: { id: book.id } }"
    class="card bg-base-100 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 cursor-pointer h-full flex flex-col"
  >
    <!-- 도서 이미지 영역 -->
    <figure class="bg-base-200 h-full overflow-hidden relative">
      <img
        v-if="book.cover"
        :src="book.cover"
        :alt="book.title"
        class="w-full h-48 object-contain"
        loading="lazy"
        @error="handleImageError"
      />
      <!-- 스켈레톤 -->
      <div v-else class="w-full h-full flex items-center justify-center text-base-content/30">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-20 w-20"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      </div>

      <!-- 순위 배지 -->
      <div class="absolute top-0 right-0 z-10" v-if="showRank && book.bestRank">
        <RankMedal :rank-number="book.bestRank" />
      </div>

      <!-- 성인 도서 뱃지 -->
      <div v-if="book.adult" class="badge badge-error absolute top-2 right-2 font-bold">19+</div>
    </figure>

    <!-- 도서 정보 영역 -->
    <div class="card-body p-4">
      <h4 class="card-title text-sm line-clamp-2 min-h-10">
        {{ book.title }}
      </h4>
      <p class="text-xs text-base-content/70 line-clamp-1">{{ book.author }}</p>

      <!-- 평점 -->
      <div class="flex items-center gap-2 mb-1">
        <div class="flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-warning"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
            />
          </svg>
          <span class="text-sm font-semibold ml-1">
            {{ formatRating(book.averageRating) }}
          </span>
        </div>
        <span class="text-xs text-base-content/50"> ({{ book.ratingRount || 0 }}) </span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import RankMedal from './RankMedal.vue'

// ==================== Props ====================
defineProps({
  book: {
    type: Object,
    required: true,
  },
  showRank: {
    type: Boolean,
    default: false,
  },
})

// ==================== Methods ====================
// 평점 포맷팅 (소수점 1자리)
const formatRating = (rating) => {
  if (!rating && rating !== 0) return '0.0'
  return Number(rating).toFixed(1)
}

// 이미지 로드 실패 시 처리
const handleImageError = (event) => {
  event.target.style.display = 'none'
}
</script>

<style scoped>
/* 텍스트 2줄 말줄임 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
