<template>
  <section>
    <LoginForm />
  </section>
</template>

<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useToastStore } from '@/stores/toastStore'
import LoginForm from './components/LoginForm.vue'

const route = useRoute()
const toastStore = useToastStore()

onMounted(async () => {
  // 인증이 필요한 페이지에서 리다이렉트된 경우
  if (route.query.authRequired === 'true') {
    // nextTick을 사용하여 컴포넌트가 완전히 마운트된 후 토스트 표시
    await nextTick()
    setTimeout(() => {
      toastStore.showToast('로그인이 필요한 서비스입니다.', 'error')
    }, 100)
  }
})
</script>
