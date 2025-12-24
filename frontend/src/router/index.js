import Layout from '@/layout/Layout.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { useLoginStore } from '@/stores/loginStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/home/HomeView.vue'),
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/accounts/LoginView.vue'),
          meta: { requiresGuest: true }, // 로그인한 사용자는 접근 불가
        },
        {
          path: 'signup',
          name: 'signup',
          component: () => import('@/views/accounts/SignupView.vue'),
          meta: { requiresGuest: true }, // 로그인한 사용자는 접근 불가
        },
        {
          path: 'books',
          name: 'books',
          component: () => import('@/views/book/BookView.vue'),
        },
        {
          path: 'books/:id',
          name: 'bookDetail',
          component: () => import('@/views/book_detail/BookDetailView.vue'),
        },
      ],
    },
    // 404 페이지
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

// 전역 네비게이션 가드
router.beforeEach((to, _from, next) => {
  const loginStore = useLoginStore()
  const isAuthenticated = !!loginStore.token

  // 인증이 필요한 페이지
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  }
  // 비로그인 사용자만 접근 가능한 페이지 (로그인, 회원가입)
  else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'home' })
  }
  // 그 외의 경우 정상 진행
  else {
    next()
  }
})

export default router
