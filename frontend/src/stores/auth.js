// frontend/src/stores/auth.js
/**
 * Pinia store для управления авторизацией.
 * Хранит токен в localStorage, предоставляет методы входа/выхода/регистрации.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

const TOKEN_KEY = 'access_token'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem(TOKEN_KEY) || null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value)

  // Actions
  /**
   * Регистрация нового пользователя
   */
  async function register(userData) {
    loading.value = true
    error.value = null
    try {
      await authAPI.register(userData)
      // После регистрации сразу логиним
      await login(userData.email, userData.password)
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Вход пользователя
   */
  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.login(email, password)
      token.value = response.data.access_token
      localStorage.setItem(TOKEN_KEY, token.value)
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Invalid email or password'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Выход пользователя
   */
  function logout() {
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  /**
   * Очистить ошибку
   */
  function clearError() {
    error.value = null
  }

  return {
    token,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    clearError,
  }
})
