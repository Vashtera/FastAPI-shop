<!-- frontend/src/views/ProfilePage.vue -->
<template>
  <main class="profile-page">
    <div class="container">

      <h1 class="page-title">My Profile</h1>

      <div v-if="loadingUser" class="loading">Loading...</div>

      <template v-else-if="authStore.user">
        <!-- Общая информация о пользователе -->
        <div class="user-card">
          <p><strong>Name:</strong> {{ authStore.user.first_name }} {{ authStore.user.last_name }}</p>
          <p><strong>Role:</strong> <span class="role-badge" :class="authStore.role">{{ authStore.role }}</span></p>
        </div>

        <!-- ===== ADMIN VIEW ===== -->
        <section v-if="authStore.isAdmin" class="section">
          <h2>Admin Panel</h2>

          <!-- Выдача роли продавца -->
          <div class="card">
            <h3>Grant Seller Role</h3>
            <div class="form-row">
              <input v-model.number="targetUserId" type="number" placeholder="User ID" />
              <button class="btn btn-dark" @click="handleGrantSeller">Grant Seller</button>
            </div>
            <p v-if="grantMessage" class="message">{{ grantMessage }}</p>
          </div>

          <!-- Создание категории -->
          <div class="card">
            <h3>Create Category</h3>
            <div class="form-row">
              <input v-model="newCategory.name" type="text" placeholder="Name" />
              <input v-model="newCategory.slug" type="text" placeholder="Slug" />
              <button class="btn btn-dark" @click="handleCreateCategory">Create</button>
            </div>
            <p v-if="categoryMessage" class="message">{{ categoryMessage }}</p>
          </div>

          <!-- Товары на модерации -->
          <div class="card">
            <h3>Pending Products ({{ pendingProducts.length }})</h3>
            <div v-if="pendingProducts.length === 0" class="empty">No products pending review.</div>
            <div v-for="product in pendingProducts" :key="product.id" class="pending-item">
              <img
                v-if="product.image_url"
                :src="product.image_url"
                :alt="product.name"
                class="pending-img"
              />
              <div class="pending-info">
                <h4>{{ product.name }}</h4>
                <p>{{ product.description }}</p>
                <p class="price">${{ product.price }}</p>
                <p class="category">Category: {{ product.category?.name }}</p>
              </div>
              <div class="pending-actions">
                <button class="btn btn-primary btn-sm" @click="handleApprove(product.id)">Approve</button>
                <button class="btn btn-outline-red btn-sm" @click="handleReject(product.id)">Reject</button>
              </div>
            </div>
          </div>
        </section>

        <!-- ===== SELLER VIEW ===== -->
        <section v-else-if="authStore.isSeller" class="section">
          <h2>Seller Panel</h2>

          <div class="card">
            <h3>Create Product</h3>
            <div class="form-column">
              <input v-model="newProduct.name" type="text" placeholder="Product name" />
              <textarea v-model="newProduct.description" placeholder="Description"></textarea>
              <input v-model.number="newProduct.price" type="number" step="0.01" placeholder="Price" />
              <select v-model.number="newProduct.category_id">
                <option disabled value="">Select category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
              <input v-model="newProduct.image_url" type="text" placeholder="Image URL (optional)" />
              <button class="btn btn-dark" @click="handleCreateProduct">Submit for review</button>
            </div>
            <p v-if="productMessage" class="message">{{ productMessage }}</p>
          </div>
        </section>

        <!-- ===== BUYER VIEW ===== -->
        <section v-else class="section">
          <h2>Account</h2>
          <div class="card">
            <p>Email associated with your account is used for order updates.</p>
            <p class="hint">Want to sell products? Contact an admin to request seller access.</p>
          </div>
        </section>
      </template>

    </div>
  </main>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authAPI, productsAPI, categoriesAPI } from '@/services/api'

const authStore = useAuthStore()
const loadingUser = ref(true)

// Admin state
const targetUserId = ref(null)
const grantMessage = ref('')
const newCategory = reactive({ name: '', slug: '' })
const categoryMessage = ref('')
const pendingProducts = ref([])

// Seller state
const categories = ref([])
const newProduct = reactive({
  name: '',
  description: '',
  price: null,
  category_id: '',
  image_url: '',
})
const productMessage = ref('')

onMounted(async () => {
  await authStore.fetchCurrentUser()
  loadingUser.value = false

  if (authStore.isAdmin) {
    await loadPendingProducts()
  }
  if (authStore.isSeller) {
    await loadCategories()
  }
})

async function loadPendingProducts() {
  try {
    const response = await productsAPI.getPending()
    pendingProducts.value = response.data
  } catch (err) {
    console.error('Error loading pending products:', err)
  }
}

async function loadCategories() {
  try {
    const response = await categoriesAPI.getAll()
    categories.value = response.data
  } catch (err) {
    console.error('Error loading categories:', err)
  }
}

async function handleGrantSeller() {
  if (!targetUserId.value) return
  try {
    await authAPI.updateRole(targetUserId.value)
    grantMessage.value = `User ${targetUserId.value} is now a seller.`
    targetUserId.value = null
  } catch (err) {
    grantMessage.value = err.response?.data?.detail || 'Failed to grant role.'
  }
}

async function handleCreateCategory() {
  try {
    await categoriesAPI.create({ name: newCategory.name, slug: newCategory.slug })
    categoryMessage.value = 'Category created.'
    newCategory.name = ''
    newCategory.slug = ''
  } catch (err) {
    categoryMessage.value = err.response?.data?.detail || 'Failed to create category.'
  }
}

async function handleApprove(productId) {
  try {
    await productsAPI.approve(productId)
    pendingProducts.value = pendingProducts.value.filter((p) => p.id !== productId)
  } catch (err) {
    console.error('Error approving product:', err)
  }
}

async function handleReject(productId) {
  try {
    await productsAPI.reject(productId)
    pendingProducts.value = pendingProducts.value.filter((p) => p.id !== productId)
  } catch (err) {
    console.error('Error rejecting product:', err)
  }
}

async function handleCreateProduct() {
  try {
    await productsAPI.create({
      name: newProduct.name,
      description: newProduct.description || null,
      price: newProduct.price,
      category_id: newProduct.category_id,
      image_url: newProduct.image_url || null,
    })
    productMessage.value = 'Product submitted for review.'
    newProduct.name = ''
    newProduct.description = ''
    newProduct.price = null
    newProduct.category_id = ''
    newProduct.image_url = ''
  } catch (err) {
    productMessage.value = err.response?.data?.detail || 'Failed to create product.'
  }
}
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 64px);
  background: #f5f5f7;
  padding: 48px 24px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #1d1d1f;
}

.loading {
  color: #86868b;
}

.user-card {
  color: #1d1d1f;
  margin: 6px 0;
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.role-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 980px;
  font-size: 13px;
  font-weight: 600;
  text-transform: capitalize;
}
.role-badge.admin { background: #ffe5e5; color: #cc0000; }
.role-badge.seller { background: #e5f2ff; color: #0071e3; }
.role-badge.buyer { background: #e8e8ed; color: #424245; }

.section h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #1d1d1f;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1d1d1f;
}

.form-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.form-column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

input, select, textarea {
  color: #1d1d1f;
  padding: 10px 14px;
  border: 1.5px solid #e8e8ed;
  border-radius: 8px;
  font-size: 14px;
  flex: 1;
  min-width: 140px;
}

textarea {
  min-height: 80px;
  resize: vertical;
}

.btn {
  padding: 10px 20px;
  border-radius: 980px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}
.btn-dark { background: #1d1d1f; color: white; }
.btn-primary { background: #0071e3; color: white; }
.btn-outline-red { background: transparent; color: #cc0000; border: 1.5px solid #cc0000; }
.btn-sm { padding: 6px 14px; font-size: 13px; }

.message {
  margin-top: 10px;
  font-size: 13px;
  color: #0071e3;
}

.empty {
  color: #86868b;
  font-size: 14px;
}

.pending-item {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e8e8ed;
}
.pending-item:first-of-type { border-top: none; }

.pending-img {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.pending-info { flex: 1; }
.pending-info h4 { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.pending-info p { font-size: 13px; color: #86868b; margin: 2px 0; }
.pending-info .price { color: #1d1d1f; font-weight: 600; }

.pending-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hint {
  font-size: 13px;
  color: #86868b;
  margin-top: 8px;
}
</style>