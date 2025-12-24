import { useLoginStore } from '@/stores/loginStore'
import { refreshToken } from '@/api/accounts'
import axios from 'axios'

// axios 인스턴스
const client = axios.create({
  baseURL: import.meta.env.VITE_SERVER_URL || 'http://localhost:8000',
  timeout: 10000, // API 응답 최대시간(10초)
})

// 요청 인터셉터: 매 요청마다 최신 토큰을 헤더에 추가
client.interceptors.request.use(
  (config) => {
    // 로그인 store 불러오기 (요청 시점에 가져오기)
    const loginStore = useLoginStore()

    // 토큰이 있으면 헤더에 추가
    if (loginStore.token) {
      config.headers.Authorization = `Bearer ${loginStore.token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 응답 인터셉터: 에러 처리 및 401 시 토큰 재발급
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    // 1. 네트워크 에러 또는 타임아웃 (서버 응답 없음)
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        console.error('요청 시간이 초과되었습니다')
      } else if (error.code === 'ERR_NETWORK') {
        console.error('네트워크 연결을 확인해주세요')
      } else {
        console.error('요청 중 오류가 발생했습니다')
      }
      return Promise.reject(error)
    }

    // 2. HTTP 상태 코드 에러 처리
    const originalRequest = error.config
    const status = error.response.status
    const errorMessage = error.response.data?.message || '오류가 발생했습니다'

    // 로그인 store 가져오기
    const loginStore = useLoginStore()

    // 401: 토큰 만료 - 재발급 시도
    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true // 무한 루프 방지

      // refresh token이 있고, 토큰 갱신 API가 아닌 경우만 재발급 시도
      if (loginStore.refreshToken && !originalRequest.url.includes('/token/refresh/')) {
        try {
          // refresh token으로 새로운 access token 발급 (API 함수 사용)
          const data = await refreshToken(loginStore.refreshToken)

          // Store 업데이트
          loginStore.updateAccessToken(data.access)

          // ROTATE_REFRESH_TOKENS가 true면 새로운 refresh token도 업데이트
          if (data.refresh) {
            loginStore.refreshToken = data.refresh
            localStorage.setItem('refresh_token', data.refresh)
          }

          // 새로운 토큰으로 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${data.access}`

          return client(originalRequest)
        } catch (refreshError) {
          // refresh token도 만료된 경우 로그아웃
          console.error('세션이 만료되었습니다. 다시 로그인해주세요.')
          loginStore.clearTokens()

          // 로그인 페이지로 이동
          // window.location.href = '/login'

          return Promise.reject(refreshError)
        }
      } else {
        // refresh token이 없는 경우 (로그인 안 한 상태)
        console.error('로그인이 필요합니다.')
        // window.location.href = '/login'
        return Promise.reject(error)
      }
    }

    // 403: 권한 없음
    if (status === 403) {
      console.error('접근 권한이 없습니다.')
    }
    // 404: 리소스 없음
    else if (status === 404) {
      console.error('요청한 리소스를 찾을 수 없습니다.')
    }
    // 500: 서버 오류
    else if (status >= 500) {
      console.error('서버에서 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
    }
    // 그 외의 에러
    else {
      console.error(errorMessage)
    }

    return Promise.reject(error)
  },
)

export default client
