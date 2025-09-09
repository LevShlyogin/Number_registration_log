// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  login: string
  fullName: string
  isAdmin: boolean
}

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const user = ref<User | null>(null)

  // --- Getters ---
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.isAdmin ?? false)

  // --- Actions ---
  // В реальном приложении здесь будет асинхронный экшен, который делает
  // запрос к /api/me (или аналогичному эндпоинту) для получения данных пользователя.
  async function fetchUser() {
    // ЗАГЛУШКА
    console.log('Fetching user data...')
    // const response = await apiClient.get('/me');
    // user.value = response.data;
    user.value = {
      login: 'yuaalekseeva',
      fullName: 'Алексеева Ю. А.',
      isAdmin: true,
    }
  }

  // Этот метод для заглушки
  function loginAs(userData: User) {
    user.value = userData
  }

  function logout() {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    fetchUser,
    loginAs,
    logout,
  }
})
