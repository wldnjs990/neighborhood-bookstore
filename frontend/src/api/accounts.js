import client from '@/api/client'
import { useLoginStore } from '@/stores/loginStore'

// 로그인 - API 호출만, 데이터 반환
export const login = async (credentials) => {
  const response = await client.post('/api/accounts/login/', credentials)
  return response.data
}

// 회원가입
export const signup = async (userData) => {
  const response = await client.post('/api/accounts/signup/', userData)
  return response.data
}

// 토큰 갱신 (인터셉터에서 사용)
export const refreshToken = async (refreshToken) => {
  const response = await client.post('/api/accounts/token/refresh/', {
    refresh: refreshToken,
  })
  return response.data
}

// 로그아웃
export const logout = async () => {
  const loginStore = useLoginStore()

  const response = await client.post('/api/accounts/logout/', {
    refresh: loginStore.refreshToken,
  })
  return response.data
}
