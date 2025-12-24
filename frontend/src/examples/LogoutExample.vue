<!-- 로그아웃 컴포넌트 사용 예시 -->
<template>
  <div>
    <button @click="handleLogout">로그아웃</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useLoginStore } from '@/stores/loginStore'
import { logout } from '@/api/accounts'

const router = useRouter()
const loginStore = useLoginStore()

const handleLogout = async () => {
  try {
    // 1. 서버에 로그아웃 요청 (선택사항)
    await logout()

    // 2. Store에서 토큰 제거
    loginStore.clearTokens()

    // 3. 로그인 페이지로 이동
    router.push('/login')

    console.log('로그아웃 성공!')
  } catch (error) {
    // 서버 요청이 실패해도 로컬 토큰은 제거
    loginStore.clearTokens()
    router.push('/login')

    console.error('로그아웃 중 오류 발생:', error)
  }
}
</script>
