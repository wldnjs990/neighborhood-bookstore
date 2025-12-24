<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-primary">404</h1>
      <p class="text-2xl font-semibold text-base-content mt-4">페이지를 찾을 수 없습니다</p>
      <p class="text-base-content/70 mt-2">요청하신 페이지가 존재하지 않거나 이동되었습니다.</p>
      <div class="mt-8">
        <router-link to="/" class="btn btn-primary">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 mr-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          홈으로 돌아가기
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// 404 페이지는 로직이 필요 없습니다
</script>
