<template>
  <main class="max-w-300 min-h-screen w-full mx-auto">
    <Navbar />
    <!-- keep-alive로 BookView 캐싱하여 뒤로가기 시 상태 유지 -->
    <!-- 모바일에서 하단 네비게이션 공간 확보 (832px 미만) -->
    <div class="min-[832px]:pb-0 pb-20">
      <RouterView v-slot="{ Component }">
        <keep-alive :include="['BookView']">
          <component :is="Component" />
        </keep-alive>
      </RouterView>
    </div>
    <!-- 모바일 하단 네비게이션 -->
    <BottomNav />
    <!-- 전역 토스트 알림 -->
    <ToastNotification />
  </main>
</template>

<script setup>
import Navbar from '@/layout/components/Navbar.vue'
import BottomNav from '@/layout/components/BottomNav.vue'
import ToastNotification from '@/components/ToastNotification.vue'
</script>
