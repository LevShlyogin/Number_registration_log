import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import apiClient from '@/api'

export interface User {
  id: number
  username: string
  is_admin: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  async function fetchUser() {
    console.log('Fetching user data...')
    try {
      const response = await apiClient.get<User>('/users/me')
      user.value = response.data
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
