<!-- frontend/src/components/CartItem.vue -->
<template>
  <div
    class="bg-white border-2 border-gray-100 rounded-none p-4 sm:p-6 shadow-sm hover:border-gray-300 transition-colors"
  >
    <!-- flex-col на мобилке, flex-row на планшете+ -->
    <div class="flex flex-col sm:flex-row gap-4 sm:gap-6">
      <!-- Изображение -->
      <div class="w-20 h-20 sm:w-24 sm:h-24 flex-shrink-0 mx-auto sm:mx-0">
        <img
          :src="item.image_url"
          :alt="item.name"
          class="w-full h-full object-cover rounded-none"
          @error="handleImageError"
        />
      </div>

      <!-- Информация -->
      <div class="flex-grow text-center sm:text-left">
        <h3 class="text-base sm:text-lg font-bold text-black mb-1 sm:mb-2">
          {{ item.name }}
        </h3>
        <p class="text-gray-600 text-sm mb-3">${{ item.price.toFixed(2) }} each</p>

        <!-- Управление количеством -->
        <div class="flex items-center justify-center sm:justify-start gap-4">
          <div class="flex items-center border-2 border-gray-100 rounded-none" style="color: black">
            <button
              @click="decreaseQuantity"
              :disabled="updating"
              class="px-3 py-2 hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4"/>
              </svg>
            </button>

            <span class="px-4 py-2 font-medium min-w-[40px] text-center">
              {{ item.quantity }}
            </span>

            <button
              @click="increaseQuantity"
              :disabled="updating"
              class="px-3 py-2 hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
              </svg>
            </button>
          </div>

          <button
            @click="handleRemove"
            :disabled="updating"
            class="text-red-600 hover:text-red-700 transition-colors disabled:opacity-50"
          >
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Сумма -->
      <div class="text-center sm:text-right pt-2 sm:pt-0">
        <p class="text-lg sm:text-xl font-bold text-black">${{ item.subtotal.toFixed(2) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'

const props = defineProps({
  item: { type: Object, required: true },
})

const cartStore = useCartStore()
const updating = ref(false)

async function increaseQuantity() {
  updating.value = true
  await cartStore.updateQuantity(props.item.product_id, props.item.quantity + 1)
  updating.value = false
}

async function decreaseQuantity() {
  updating.value = true
  if (props.item.quantity > 1) {
    await cartStore.updateQuantity(props.item.product_id, props.item.quantity - 1)
  } else {
    await cartStore.removeFromCart(props.item.product_id)
  }
  updating.value = false
}

async function handleRemove() {
  updating.value = true
  await cartStore.removeFromCart(props.item.product_id)
  updating.value = false
}

function handleImageError(event) {
  event.target.src = 'https://via.placeholder.com/100x100?text=No+Image'
}
</script>