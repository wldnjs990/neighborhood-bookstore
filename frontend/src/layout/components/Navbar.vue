<template>
  <div class="navbar bg-base-100 shadow-sm">
    <!-- 홈 버튼 -->
    <div class="flex-1">
      <RouterLink :to="{ name: 'home' }" class="btn btn-ghost text-xl">동네책방</RouterLink>
      <!-- 데스크톱에서만 표시 (832px 이상) -->
      <RouterLink
        :to="{ name: 'bookSearch' }"
        class="btn btn-ghost text-md hidden min-[832px]:inline-flex"
      >
        <MagnifyingGlassIcon class="w-5" />도서 검색
      </RouterLink>
      <RouterLink
        :to="{ name: 'aiRecommend' }"
        class="btn btn-ghost text-md hidden min-[832px]:inline-flex"
      >
        <BookOpenIcon class="w-5" />책방 할아버지께 물어봐!
      </RouterLink>
      <RouterLink
        :to="{ name: 'trade' }"
        class="btn btn-ghost text-md hidden min-[832px]:inline-flex"
      >
        <BuildingStorefrontIcon class="w-5" />중고책 거래
      </RouterLink>
    </div>

    <!-- 우측 버튼 -->
    <div class="flex-none">
      <ul class="menu menu-horizontal px-1 flex items-center">
        <!-- 로그인 -->
        <li v-if="!loginStore.token">
          <RouterLink to="/login">로그인</RouterLink>
        </li>
        <!-- 회원정보 셀렉터 -->
        <li v-if="loginStore.token">
          <details ref="detailsRef">
            <summary class="text-sm md:text-base">
              어서오세요 {{ loginStore.user?.nickname || '익명' }}님!
            </summary>
            <ul class="w-full bg-base-100 rounded-t-none p-2 z-10">
              <li><RouterLink :to="{ name: 'profile' }" @click="closeDropdown">내 프로필</RouterLink></li>
              <li><a @click="handleLogout">로그아웃</a></li>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useLoginStore } from '@/stores/loginStore'
import ThemeController from './ThemeController.vue'
import { logout } from '@/api/accounts'
import { useRouter } from 'vue-router'
import {
  BookOpenIcon,
  BuildingStorefrontIcon,
  MagnifyingGlassIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const loginStore = useLoginStore()
const detailsRef = ref(null)

const closeDropdown = () => {
  if (detailsRef.value) {
    detailsRef.value.removeAttribute('open')
  }
}

const handleClickOutside = (event) => {
  if (detailsRef.value && !detailsRef.value.contains(event.target)) {
    closeDropdown()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleLogout = async () => {
  closeDropdown()
  try {
    // 1. 먼저 서버에 로그아웃 요청 (토큰 블랙리스트 등록)
    await logout()

    // 2. 성공하면 로컬 토큰 제거
    loginStore.clearTokens()

    // 3. 로그인 페이지로 이동
    router.push('/login')
  } catch (error) {
    // 에러가 나도 로컬 토큰은 제거 (이미 만료되었거나 무효한 토큰일 수 있음)
    console.error('로그아웃 실패:', error)
    loginStore.clearTokens()
  }
}
</script>
