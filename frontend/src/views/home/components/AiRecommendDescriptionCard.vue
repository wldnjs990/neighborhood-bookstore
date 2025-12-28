<template>
  <div class="card-body p-12 flex flex-col justify-center">
    <p class="text-lg text-base-content/80 mb-6 leading-relaxed">
      60년 동안 책과 함께한 동네책방 할아버지가<br />
      당신에게 딱 맞는 책을 골라드립니다
    </p>

    <!-- 특징 리스트 -->
    <div class="space-y-3 mb-8">
      <template :key="prop.title" v-for="prop in featureItemProps">
        <AiRecommendFeatureItem :title="prop.title" :content="prop.content" />
      </template>
    </div>

    <!-- CTA 버튼 -->
    <button @click="goToAIRecommend" class="btn btn-primary btn-lg w-full group">
      <ChatBubbleOvalLeftEllipsisIcon class="h-6 w-6 group-hover:animate-bounce" />
      할아버지께 물어보러 가기
      <ChevronRightIcon class="h-5 w-5 group-hover:translate-x-1 transition-transform" />
    </button>

    <!-- 안내 문구 -->
    <p class="text-xs text-center text-base-content/50 mt-4">
      💡 로그인하면 Book MBTI 기반 추천을 받을 수 있어요
    </p>
  </div>
</template>

<script setup>
import { ChatBubbleOvalLeftEllipsisIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'

import { useRouter } from 'vue-router'
import AiRecommendFeatureItem from './AiRecommendFeatureItem.vue'

const router = useRouter()

const goToAIRecommend = () => {
  router.push({ name: 'aiRecommend' })
}

// AI 추천 섹션 특징 아이템 데이터
const featureItemProps = [
  { title: 'AI 기반 맞춤 추천', content: '당신의 독서 취향을 분석해 최적의 책 3권 추천' },
  { title: '따뜻한 할아버지의 조언', content: '오랜 경험으로 책을 고르는 이유를 친절히 설명' },
  { title: '무료 서비스', content: '언제든지 할아버지께 물어보세요!' },
]
</script>
