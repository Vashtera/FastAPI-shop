// frontend/src/services/api.js
/**
 * API сервис для взаимодействия с backend.
 * Централизует все HTTP запросы к FastAPI серверу.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерсептор — добавляет токен к каждому запросу если он есть
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * API методы для авторизации
 */
export const authAPI = {
  register(userData) {
    return apiClient.post('/users/registration/', userData)
  },

  login(email, password) {
    // OAuth2 требует form-data, не JSON
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    return apiClient.post('/users/login/', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
}

/**
 * API методы для работы с товарами
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
}

/**
 * API методы для работы с категориями
 */
export const categoriesAPI = {
  getAll() {
    return apiClient.get('/api/categories')
  },

  getById(id) {
    return apiClient.get(`/api/categories/${id}`)
  },
}

/**
 * API методы для работы с корзиной
 */
export const cartAPI = {
  addItem(item, cartData) {
    return apiClient.post('/api/cart/add', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  getCart(cartData) {
    return apiClient.get('/api/cart', { data: cartData })
  },

  updateItem(item, cartData) {
    return apiClient.put('/api/cart/update', {
      product_id: item.product_id,
      quantity: item.quantity,
      cart: cartData,
    })
  },

  removeItem(productId, cartData) {
    return apiClient.delete(`/api/cart/remove/${productId}`, {
      data: { cart: cartData },
    })
  },
}

export default apiClient
