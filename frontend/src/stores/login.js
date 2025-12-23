import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useLoginStore = defineStore('login', () => {
  // localStorage에서 토큰 불러오기
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 로그인
  async function login(credentials) {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_SERVER_URL || 'http://localhost:8000'}/accounts/login/`,
        credentials,
      )

      // Simple JWT는 access와 refresh 키로 반환
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      user.value = response.data.user || null

      // localStorage에 저장
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }

      return response.data
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  // 토큰 재발급 (refresh token 사용)
  async function refresh() {
    try {
      // refresh token으로 새로운 access token 발급
      const response = await axios.post(
        `${import.meta.env.VITE_SERVER_URL || 'http://localhost:8000'}/accounts/token/refresh/`,
        {
          refresh: refreshToken.value, // refresh token 전송
        },
      )

      // 새로운 access token 저장
      token.value = response.data.access
      localStorage.setItem('access_token', response.data.access)

      // ROTATE_REFRESH_TOKENS가 true면 새로운 refresh token도 반환됨
      if (response.data.refresh) {
        refreshToken.value = response.data.refresh
        localStorage.setItem('refresh_token', response.data.refresh)
      }

      return response.data
    } catch (error) {
      console.error('Token refresh failed:', error)
      // refresh token도 만료된 경우
      logout()
      throw error
    }
  }

  // 로그아웃
  function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return {
    token,
    refreshToken,
    user,
    login,
    refresh,
    logout,
  }
})
