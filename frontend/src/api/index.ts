import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Добавляем Interceptor (перехватчик) для запросов
apiClient.interceptors.request.use(
  (config) => {
    // Получаем authStore ВНУТРИ interceptor-а, а не снаружи,
    // чтобы избежать проблем с порядком инициализации Pinia.
    const authStore = useAuthStore()

    // Если пользователь залогинен (т.е. у нас есть его login), добавляем заголовок
    if (authStore.user?.login) {
      config.headers['X-User'] = authStore.user.login
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Interceptor для ответов (полезен для глобальной обработки ошибок)
apiClient.interceptors.response.use(
  (response) => {
    // Просто возвращаем успешный ответ
    return response
  },
  (error) => {
    // Здесь можно обрабатывать глобальные ошибки, например 401/403,
    // показывать уведомления и т.д.
    console.error('Axios error:', error.response?.data || error.message)
    // Возвращаем ошибку, чтобы useQuery/useMutation могли ее поймать
    return Promise.reject(error)
  },
)

export default apiClient
