<template>
  <section class="flex min-h-screen items-center justify-center">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-md">
      <div class="text-center">
        <h1 class="text-3xl font-bold">로그인</h1>
        <p class="mt-2 text-gray-600">계정에 로그인하세요</p>
      </div>

      <form @submit.prevent="handleLogin" class="mt-8 space-y-6">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700"> 아이디 </label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="아이디를 입력하세요"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700"> 비밀번호 </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="비밀번호를 입력하세요"
            />
          </div>
        </div>

        <div v-if="errorMessage" class="text-sm text-red-600">
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>

        <div class="text-center text-sm">
          <span class="text-gray-600">계정이 없으신가요?</span>
          <router-link to="/signup" class="ml-1 font-medium text-blue-600 hover:text-blue-500">
            회원가입
          </router-link>
        </div>
      </form>
    </div>
  </section>
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
const errorMessage = ref('')

const handleLogin = async () => {
  // 에러 메시지 초기화
  errorMessage.value = ''
  isLoading.value = true

  try {
    // 1. API 호출
    const data = await login({
      username: username.value,
      password: password.value,
    })

    // 2. Store에 토큰 저장
    loginStore.setTokens(data.access, data.refresh)

    // 3. 사용자 정보가 있다면 저장
    if (data.user) {
      loginStore.user = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
    }

    // 4. 홈 페이지로 이동
    router.push('/')
  } catch (error) {
    // 에러 처리
    console.error('로그인 실패:', error)
    errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>
