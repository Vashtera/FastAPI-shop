// frontend/src/stores/auth.js
/**
 * Pinia store для управления авторизацией.
 * Хранит токен и данные текущего пользователя (включая роль).
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

const TOKEN_KEY = 'access_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || null)
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const role = computed(() => user.value?.role || null)
  const isAdmin = computed(() => role.value === 'admin')
  const isSeller = computed(() => role.value === 'seller')

  /**
   * Получить данные текущего пользователя (включая роль) с сервера
   */
  async function fetchCurrentUser() {
    if (!token.value) return
    try {
      const response = await authAPI.getMe()
      user.value = response.data
    } catch (err) {
      console.error('Error fetching current user:', err)
      // токен невалиден — разлогиниваем
      logout()
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null
    try {
      await authAPI.register(userData)
      await login(userData.email, userData.password)
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.login(email, password)
      token.value = response.data.access_token
      localStorage.setItem(TOKEN_KEY, token.value)
      await fetchCurrentUser()
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Invalid email or password'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  function clearError() {
    error.value = null
  }

  return {
    token,
    user,
    loading,
    error,
    isAuthenticated,
    role,
    isAdmin,
    isSeller,
    fetchCurrentUser,
    register,
    login,
    logout,
    clearError,
  }
})