<!-- frontend/src/views/LoginPage.vue -->
<template>
  <main class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md">

      <!-- Заголовок -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-black">Sign in</h1>
        <p class="text-gray-500 mt-1">Welcome back</p>
      </div>

      <!-- Форма -->
      <form @submit.prevent="handleLogin" class="bg-white border-2 border-black p-8 space-y-5">

        <!-- Ошибка -->
        <div v-if="authStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {{ authStore.error }}
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-semibold text-black mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="you@example.com"
            class="w-full border-2 border-black px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-semibold text-black mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="••••••••"
            class="w-full border-2 border-black px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-black text-white py-3 font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ authStore.loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <!-- Ссылка на регистрацию -->
      <p class="text-center text-gray-500 mt-6 text-sm">
        Don't have an account?
        <router-link to="/register" class="text-black font-semibold underline hover:no-underline">
          Create one
        </router-link>
      </p>

    </div>
  </main>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const form = reactive({
  email: '',
  password: '',
})

async function handleLogin() {
  authStore.clearError()
  const success = await authStore.login(form.email, form.password)
  if (success) {
    router.push({ name: 'home' })
  }
}
</script>
