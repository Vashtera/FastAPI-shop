// frontend/src/stores/cart.js
/**
 * Pinia store для управления корзиной покупок.
 * Корзина хранится на сервере в Redis, привязана к user_id
 * через токен авторизации — здесь только запросы к API.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { cartAPI } from '@/services/api'

export const useCartStore = defineStore('cart', () => {
  const cartDetails = ref(null)
  const loading = ref(false)

  const itemsCount = computed(() => cartDetails.value?.items_count || 0)
  const totalPrice = computed(() => cartDetails.value?.total || 0)
  const hasItems = computed(() => (cartDetails.value?.items?.length || 0) > 0)

  /**
   * Получить корзину с сервера
   */
  async function fetchCartDetails() {
    loading.value = true
    try {
      const response = await cartAPI.getCart()
      cartDetails.value = response.data
    } catch (err) {
      console.error('Error fetching cart details:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Добавить товар в корзину
   */
  async function addToCart(productId, quantity = 1) {
    try {
      await cartAPI.addItem(productId, quantity)
      await fetchCartDetails()
      return true
    } catch (err) {
      console.error('Error adding to cart:', err)
      return false
    }
  }

  /**
   * Обновить количество товара
   */
  async function updateQuantity(productId, quantity) {
    if (quantity <= 0) {
      return removeFromCart(productId)
    }
    try {
      await cartAPI.updateItem(productId, quantity)
      await fetchCartDetails()
      return true
    } catch (err) {
      console.error('Error updating cart:', err)
      return false
    }
  }

  /**
   * Удалить товар из корзины
   */
  async function removeFromCart(productId) {
    try {
      await cartAPI.removeItem(productId)
      await fetchCartDetails()
      return true
    } catch (err) {
      console.error('Error removing from cart:', err)
      return false
    }
  }

  return {
    cartDetails,
    loading,
    itemsCount,
    totalPrice,
    hasItems,
    fetchCartDetails,
    addToCart,
    updateQuantity,
    removeFromCart,
  }
})