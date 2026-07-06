// frontend/src/router/index.js
/**
 * Конфигурация Vue Router.
 * Определяет маршруты приложения и защищает роуты требующие авторизации.
 */

import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import ProductDetailPage from '@/views/ProductDetailPage.vue'
import CartPage from '@/views/CartPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import RegisterPage from '@/views/RegisterPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { title: 'Shop — Catalog' },
    },
    {
      path: '/product/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: { title: 'Product Details' },
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartPage,
      meta: { title: 'Shopping Cart' },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { title: 'Sign In', guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: { title: 'Create Account', guestOnly: true },
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'FastAPI Shop'

  const token = localStorage.getItem('access_token')

  // Если страница только для гостей (login/register) и пользователь уже залогинен
  if (to.meta.guestOnly && token) {
    return next({ name: 'home' })
  }

  next()
})

export default router
