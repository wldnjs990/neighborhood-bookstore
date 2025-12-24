<!-- 로그인 컴포넌트 사용 예시 -->
<template>
  <div>
    <form @submit.prevent="handleLogin">
      <input v-model="username" type="text" placeholder="아이디" />
      <input v-model="password" type="password" placeholder="비밀번호" />
      <button type="submit" :disabled="isLoading">로그인</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLoginStore } from '@/stores/loginStore'
import { login } from '@/api/accounts'

const router = useRouter()
const loginStore = useLoginStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true

  try {
    // 1. API 호출 (accounts.js)
    const data = await login({
      username: username.value,
      password: password.value,
    })

    // 2. Store에 토큰 저장 (loginStore.js)
    loginStore.setTokens(data.access, data.refresh)

    // 3. 사용자 정보가 있다면 저장
    if (data.user) {
      loginStore.user = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
    }

    // 4. 홈 페이지로 이동
    router.push('/')

    console.log('로그인 성공!')
  } catch (error) {
    // 에러 처리 (인터셉터가 이미 로깅)
    alert('로그인에 실패했습니다')
  } finally {
    isLoading.value = false
  }
}
</script>
