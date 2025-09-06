import axios from 'axios'
import type { AxiosInstance } from 'axios'

const FAKE_X_USER = 'yuaalekseeva'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor (перехватчик) для добавления заголовка X-User ко всем запросам
apiClient.interceptors.request.use(
  (config) => {
    // Здесь мы будем брать пользователя из Pinia-стора
    // const authStore = useAuthStore();
    // if (authStore.username) {
    //   config.headers['X-User'] = authStore.username;
    // }
    config.headers['X-User'] = FAKE_X_USER // Пока используем заглушку
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

export default apiClient
