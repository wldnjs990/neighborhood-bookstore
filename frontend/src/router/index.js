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
          path: 'books',
          name: 'bookSearch',
          component: () => import('@/views/book/BookView.vue'),
        },
        {
          path: 'books/detail/:id',
          name: 'bookDetail',
          component: () => import('@/views/book_detail/BookDetailView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/profile/ProfileView.vue'),
          meta: { requiresAuth: true }, // 로그인 필요
        },
        {
          path: 'ai-recommend',
          name: 'aiRecommend',
          component: () => import('@/views/ai_recommend/AIRecommendView.vue'),
          meta: { requiresAuth: true }, // 로그인 필요
        },
        {
          path: 'trade',
          name: 'trade',
          component: () => import('@/views/trade/TradeView.vue'),
        },
        {
          path: 'trade/detail/:id',
          name: 'tradeDetail',
          component: () => import('@/views/trade_detail/TradeDetailView.vue'),
        },
        {
          path: 'trade/create',
          name: 'tradeCreate',
          component: () => import('@/views/trade_create/TradeCreateView.vue'),
          meta: { requiresAuth: true }, // 로그인 필요
        },
        {
          path: 'trade/edit/:id',
          name: 'tradeEdit',
          component: () => import('@/views/trade_edit/TradeEditView.vue'),
          meta: { requiresAuth: true }, // 로그인 필요
        },
      ],
    },
    // 404 페이지
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFoundView.vue'),
    },
    // 로그인/회원가입 페이지
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { requiresGuest: true }, // 로그인한 사용자는 접근 불가
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/signup/SignupView.vue'),
      meta: { requiresGuest: true }, // 로그인한 사용자는 접근 불가
    },
    // 온보딩 페이지
    {
      path: '/onboard',
      name: 'onboard',
      component: () => import('@/views/onboard/OnboardView.vue'),
    },
  ],
})

// 전역 네비게이션 가드
router.beforeEach((to, _from, next) => {
  const loginStore = useLoginStore()
  const isAuthenticated = loginStore.token
  const user = loginStore.user

  // 인증이 필요한 페이지
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath, authRequired: 'true' } })
    return
  }

  // 비로그인 사용자만 접근 가능한 페이지 (로그인, 회원가입)
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'home' })
    return
  }

  // 로그인한 사용자가 온보딩 페이지가 아닌 곳으로 이동할 때
  // MBTI 정보가 없으면 온보딩 페이지로 리다이렉트
  if (isAuthenticated && user && !user.bookMbti && to.name !== 'onboard') {
    next({ name: 'onboard' })
    return
  }

  // 그 외의 경우 정상 진행
  next()
})

export default router
