import Layout from '@/layout/Layout.vue'
import { createRouter, createWebHistory } from 'vue-router'

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
          component: () => import('@/views/HomeView.vue'),
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/LoginView.vue'),
        },
        {
          path: 'signup',
          name: 'signup',
          component: () => import('@/views/SignupView.vue'),
        },
      ],
    },
  ],
})

export default router
