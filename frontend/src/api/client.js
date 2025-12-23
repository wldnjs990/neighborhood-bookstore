import { useLoginStore } from '@/stores/login'
import axios from 'axios'

// axios 인스턴스
const client = axios.create({
  baseURL: import.meta.env.VITE_SERVER_URL || 'http://localhost:8000',
  timeout: 10000,
})

// 요청 인터셉터: 매 요청마다 최신 토큰을 헤더에 추가
client.interceptors.request.use(
  (config) => {
    const loginStore = useLoginStore()

    // 토큰이 있으면 헤더에 추가
    if (loginStore.token) {
      config.headers.Authorization = `Bearer ${loginStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 401 에러 시 토큰 재발급
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 에러이고, 재시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true // 무한 루프 방지

      const loginStore = useLoginStore()

      try {
        // refresh token으로 새로운 access token 발급
        await loginStore.refresh()

        // 새로운 토큰으로 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${loginStore.token}`
        return client(originalRequest)
      } catch (refreshError) {
        // refresh token도 만료된 경우 로그아웃
        loginStore.logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default client
