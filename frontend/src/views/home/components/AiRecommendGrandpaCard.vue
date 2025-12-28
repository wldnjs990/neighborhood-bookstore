<template>
  <div
    class="bg-linear-to-br from-amber-100 to-orange-200 dark:from-amber-900/50 dark:to-orange-900/50 flex items-center justify-center p-12 relative overflow-hidden"
  >
    <!-- 배경 장식 -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-10 left-10 text-6xl">📚</div>
      <div class="absolute bottom-10 right-10 text-6xl">📖</div>
      <div class="absolute top-1/2 left-1/4 text-4xl">✨</div>
    </div>

    <!-- 할아버지 캐릭터 -->
    <div class="relative z-10 text-center">
      <div
        class="w-48 h-48 mx-auto mb-6 rounded-full bg-linear-to-br from-amber-200 to-orange-300 flex items-center justify-center shadow-xl border-8 border-white/50 animate-float"
      >
        <div class="text-8xl">👴</div>
      </div>
      <div class="space-y-2">
        <p class="text-2xl font-bold text-amber-900 dark:text-amber-100">동네책방</p>
        <p class="text-xl text-amber-800 dark:text-amber-200">할아버지</p>
        <div class="badge badge-warning gap-2 text-sm px-4 py-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          60년 경력
        </div>
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
/* 할아버지 이미지 떠다니는 애니메이션 */
@keyframes float {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style>
