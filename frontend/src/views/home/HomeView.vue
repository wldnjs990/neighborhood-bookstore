<template>
  <main class="px-5">
    <!-- AI 도서 추천 섹션 -->
    <AiRecommendSection />

    <!-- 도서 리스트 섹션 -->
    <BookListSection />

    <!-- 최신 중고거래 섹션 -->
    <RecentTradesSection />
  </main>
</template>

<script setup>
import AiRecommendSection from './components/AiRecommendSection.vue'
import BookListSection from './components/BookListSection.vue'
import RecentTradesSection from './components/RecentTradesSection.vue'
</script>
