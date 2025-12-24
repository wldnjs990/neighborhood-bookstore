import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useLoginStore = defineStore('login', () => {
  // localStorage에서 토큰 불러오기
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 토큰 저장
  const setTokens = (accessToken, newRefreshToken) => {
    token.value = accessToken
    refreshToken.value = newRefreshToken

    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', newRefreshToken)
  }

  // Access 토큰만 업데이트
  const updateAccessToken = (accessToken) => {
    token.value = accessToken
    localStorage.setItem('access_token', accessToken)
  }

  // 로그아웃 (토큰 제거)
  const clearTokens = () => {
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
    setTokens,
    updateAccessToken,
    clearTokens,
  }
})
