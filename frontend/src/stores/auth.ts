import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import axios from 'axios'
import apiClient from '@/api'
import router from '@/router'

export interface User {
  id: number
  username: string
  is_admin: boolean
}

// Берем URL сервиса авторизации из переменных окружения
const AUTH_URL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8001'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)
  const fullName = computed(() => user.value?.username || '...')

  /**
   * Логин:
   * 1. Отправляем логин/пароль на Auth Service.
   * 2. Получаем токен.
   * 3. Сохраняем токен.
   * 4. Запрашиваем профиль у API Журнала.
   */
  async function login(username: string, password: string) {
    try {
      // Формат x-www-form-urlencoded (требование OAuth2)
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)

      const response = await axios.post(`${AUTH_URL}/auth/login`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      const { access_token } = response.data

      token.value = access_token
      localStorage.setItem('access_token', access_token)

      await fetchUser()

      return true
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  async function fetchUser() {
    if (!token.value) return null
    try {
      // Запрашиваем /users/me у API Журнала (он проверит токен и вернет роль)
      const response = await apiClient.get<User>('/users/me')
      user.value = response.data
      return user.value
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
      return null
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
    router.push('/login').then()
  }

  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    fullName,
    login,
    logout,
    fetchUser,
  }
})
