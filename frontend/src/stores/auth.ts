import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

// import apiClient from '@/api' // Раскомментируем, когда будет реальный API

export interface User {
  login: string
  fullName: string
  isAdmin: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.isAdmin ?? false)

  // Асинхронный экшен для получения данных пользователя
  async function fetchUser() {
    console.log('Fetching user data...')
    try {
      // --- ЗАГЛУШКА API-ЗАПРОСА ---
      await new Promise((resolve) => setTimeout(resolve, 500)) // Имитация задержки сети
      user.value = {
        login: 'yuaalekseeva',
        fullName: 'Алексеева Ю. А.',
        isAdmin: true,
      }
      // --- КОНЕЦ ЗАГЛУШКИ ---
      return user.value
    } catch (error) {
      console.error('Failed to fetch user:', error)
      user.value = null
      return null
    }
  }

  function logout() {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    isAdmin,
    fetchUser,
    logout,
  }
})
