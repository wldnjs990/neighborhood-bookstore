<template>
  <section class="flex min-h-screen items-center justify-center">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-md">
      <div class="text-center">
        <h1 class="text-3xl font-bold">회원가입</h1>
        <p class="mt-2 text-gray-600">새 계정을 만드세요</p>
      </div>

      <form @submit.prevent="handleSignup" class="mt-8 space-y-6">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              아이디 <span class="text-red-500">*</span>
            </label>
            <input
              id="username"
              v-model="username"
              type="text"
              required
              minlength="3"
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="아이디 (3자 이상)"
            />
          </div>

          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              이메일 <span class="text-red-500">*</span>
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="example@email.com"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              비밀번호 <span class="text-red-500">*</span>
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              minlength="8"
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="비밀번호 (8자 이상)"
            />
          </div>

          <div>
            <label for="passwordConfirm" class="block text-sm font-medium text-gray-700">
              비밀번호 확인 <span class="text-red-500">*</span>
            </label>
            <input
              id="passwordConfirm"
              v-model="passwordConfirm"
              type="password"
              required
              minlength="8"
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="비밀번호 재입력"
            />
          </div>

          <div>
            <label for="nickname" class="block text-sm font-medium text-gray-700"> 닉네임 </label>
            <input
              id="nickname"
              v-model="nickname"
              type="text"
              class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="닉네임 (선택사항)"
            />
          </div>
        </div>

        <div v-if="errorMessage" class="text-sm text-red-600">
          {{ errorMessage }}
        </div>

        <div v-if="successMessage" class="text-sm text-green-600">
          {{ successMessage }}
        </div>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400"
        >
          {{ isLoading ? '가입 중...' : '회원가입' }}
        </button>

        <div class="text-center text-sm">
          <span class="text-gray-600">이미 계정이 있으신가요?</span>
          <router-link to="/login" class="ml-1 font-medium text-blue-600 hover:text-blue-500">
            로그인
          </router-link>
        </div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { signup } from '@/api/accounts'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const nickname = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleSignup = async () => {
  // 초기화
  errorMessage.value = ''
  successMessage.value = ''

  // 비밀번호 일치 확인
  if (password.value !== passwordConfirm.value) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }

  // 비밀번호 길이 확인
  if (password.value.length < 8) {
    errorMessage.value = '비밀번호는 8자 이상이어야 합니다.'
    return
  }

  isLoading.value = true

  try {
    // 회원가입 API 호출
    await signup({
      username: username.value,
      email: email.value,
      password: password.value,
      passwordConfirm: passwordConfirm.value,  // camelCase (자동 변환됨)
      nickname: nickname.value || username.value, // 닉네임이 없으면 아이디 사용
    })

    // 성공 메시지
    successMessage.value = '회원가입이 완료되었습니다. 로그인 페이지로 이동합니다...'

    // 2초 후 로그인 페이지로 이동
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (error) {
    console.error('회원가입 실패:', error)

    // 서버에서 온 에러 메시지 처리
    if (error.response?.data) {
      const errorData = error.response.data

      // Django REST Framework 에러 형식 (camelCase로 자동 변환됨)
      if (errorData.username) {
        errorMessage.value = `아이디: ${errorData.username[0]}`
      } else if (errorData.email) {
        errorMessage.value = `이메일: ${errorData.email[0]}`
      } else if (errorData.password) {
        errorMessage.value = `비밀번호: ${errorData.password[0]}`
      } else if (errorData.passwordConfirm) {
        errorMessage.value = `비밀번호 확인: ${errorData.passwordConfirm[0]}`
      } else if (errorData.nonFieldErrors) {
        errorMessage.value = errorData.nonFieldErrors[0]
      } else {
        // 전체 에러 메시지 표시 (디버깅용)
        const errorMessages = Object.entries(errorData)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
          .join(', ')
        errorMessage.value = errorMessages || '회원가입에 실패했습니다. 다시 시도해주세요.'
      }
    } else {
      errorMessage.value = '회원가입에 실패했습니다. 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>
