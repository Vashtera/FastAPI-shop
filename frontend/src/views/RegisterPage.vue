<!-- frontend/src/views/RegisterPage.vue -->
<template>
  <main class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-md">

      <!-- Заголовок -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-black">Create account</h1>
        <p class="text-gray-500 mt-1">Join FastAPI Shop</p>
      </div>

      <!-- Форма -->
      <form @submit.prevent="handleRegister" class="bg-white border-2 border-black p-8 space-y-5">

        <!-- Ошибка -->
        <div v-if="authStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 text-sm">
          {{ authStore.error }}
        </div>

        <!-- First name + Last name -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-semibold text-black mb-1">First name</label>
            <input
              v-model="form.first_name"
              type="text"
              required
              minlength="2"
              placeholder="John"
              class="w-full border-2 border-black px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-black mb-1">Last name</label>
            <input
              v-model="form.last_name"
              type="text"
              required
              minlength="2"
              placeholder="Doe"
              class="w-full border-2 border-black px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>
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
            minlength="8"
            placeholder="Min 8 characters"
            class="w-full border-2 border-black px-4 py-3 text-black placeholder-gray-400 focus:outline-none focus:border-gray-500 transition-colors"
          />
        </div>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-black text-white py-3 font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ authStore.loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <!-- Ссылка на вход -->
      <p class="text-center text-gray-500 mt-6 text-sm">
        Already have an account?
        <router-link to="/login" class="text-black font-semibold underline hover:no-underline">
          Sign in
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
  first_name: '',
  last_name: '',
  email: '',
  password: '',
})

async function handleRegister() {
  authStore.clearError()
  const success = await authStore.register(form)
  if (success) {
    router.push({ name: 'home' })
  }
}
</script>
