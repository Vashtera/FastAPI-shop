// frontend/src/services/api.js
/**
 * API сервис для взаимодействия с backend.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Авторизация и профиль
 */
export const authAPI = {
  register(userData) {
    return apiClient.post('/users/registration/', userData)
  },

  login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return apiClient.post('/users/login/', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  getMe() {
    return apiClient.get('/users/me/')
  },

  updateRole(userId) {
    return apiClient.put('/users/update_role/', null, {
      params: { user_id: userId },
    })
  },
}

/**
 * Товары
 */
export const productsAPI = {
  getAll() {
    return apiClient.get('/api/products')
  },

  getById(id) {
    return apiClient.get(`/api/products/${id}`)
  },

  getByCategory(categoryId) {
    return apiClient.get(`/api/products/category/${categoryId}`)
  },

  create(productData) {
    return apiClient.post('/api/products/add', productData)
  },

  getPending() {
    return apiClient.get('/api/products/admin/products/pending')
  },

  approve(productId) {
    return apiClient.put(`/api/products/admin/products/${productId}/approve`)
  },

  reject(productId) {
    return apiClient.put(`/api/products/admin/products/${productId}/reject`)
  },
}

/**
 * Категории
 */
export const categoriesAPI = {
  getAll() {
    return apiClient.get('/api/categories')
  },

  getById(id) {
    return apiClient.get(`/api/categories/${id}`)
  },

  create(categoryData) {
    return apiClient.post('/api/categories/add', categoryData)
  },
}

/**
 * Корзина
 */
export const cartAPI = {
  addItem(productId, quantity) {
    return apiClient.post('/api/cart/add', null, {
      params: { product_id: productId, quantity: quantity },
    })
  },

  getCart() {
    return apiClient.get('/api/cart')
  },

  updateItem(productId, quantity) {
    return apiClient.put('/api/cart/update', null, {
      params: { product_id: productId, quantity: quantity },
    })
  },

  removeItem(productId) {
    return apiClient.delete(`/api/cart/remove/${productId}`)
  },
}

export default apiClient