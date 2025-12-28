<template>
  <!-- ==================== 할아버지 AI 추천 홍보 섹션 ==================== -->
  <section class="py-16 dark:from-amber-950/20 dark:to-orange-950/20">
    <div class="flex flex-col items-center gap-3 mb-10">
      <h2 class="text-3xl font-bold">책방 할아버지께 물어봐!</h2>
    </div>
    <!-- 할아버지 추천 섹션 카드 -->
    <div class="container mx-auto px-4">
      <div class="card bg-base-100 shadow-2xl overflow-hidden max-w-5xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-0">
          <!-- 왼쪽: 할아버지 이미지 영역 -->
          <AiRecommendGrandpaCard />

          <!-- 오른쪽: 설명 및 버튼 영역 -->
          <AiRecommendDescriptionCard />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import AiRecommendDescriptionCard from './AiRecommendDescriptionCard.vue'
import AiRecommendGrandpaCard from './AiRecommendGrandpaCard.vue'
</script>
