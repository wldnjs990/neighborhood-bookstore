<template>
  <div class="navbar bg-base-100 shadow-sm">
    <!-- 홈 버튼 -->
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">daisyUI</a>
    </div>

    <!-- 우측 버튼 -->
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1">
        <!-- 로그인 -->
        <li>
          <a @click="handleLogout" v-if="loginStore.token">로그아웃</a>
          <RouterLink to="/login" v-else>로그인</RouterLink>
        </li>
        <!-- 회원정보 셀렉터 -->
        <li>
          <details>
            <summary>반갑습니다! ___님!</summary>
            <ul class="bg-base-100 rounded-t-none p-2">
              <li><a>내 프로필</a></li>
            </ul>
          </details>
        </li>
        <li>
          <ThemeController />
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useLoginStore } from '@/stores/loginStore'
import ThemeController from './ThemeController.vue'
import { logout } from '@/api/accounts'

const loginStore = useLoginStore()

const handleLogout = async () => {
  try {
    // 1. 먼저 서버에 로그아웃 요청 (토큰 블랙리스트 등록)
    await logout()

    // 2. 성공하면 로컬 토큰 제거
    loginStore.clearTokens()
  } catch (error) {
    // 에러가 나도 로컬 토큰은 제거 (이미 만료되었거나 무효한 토큰일 수 있음)
    console.error('로그아웃 실패:', error)
    loginStore.clearTokens()
  }
}
</script>
