import { ref } from 'vue'

// Создаем состояние на уровне модуля, чтобы оно было синглтоном
const show = ref(false)
const text = ref('')
const color = ref('info')
const timeout = ref(4000)

export function useNotifier() {
  const notify = (
    message: string,
    notificationColor: string = 'info',
    notificationTimeout: number = 4000,
  ) => {
    text.value = message
    color.value = notificationColor
    timeout.value = notificationTimeout
    show.value = true
  }

  // Удобные шорткаты
  const success = (message: string) => notify(message, 'success')
  const error = (message: string) => notify(message, 'error', 6000) // Ошибки показываем дольше
  const info = (message: string) => notify(message, 'info')
  const warning = (message: string) => notify(message, 'warning')

  return {
    show, // Реактивное состояние для v-model
    text, // Текст уведомления
    color, // Цвет уведомления
    timeout, // Время показа
    success,
    error,
    info,
    warning,
  }
}
