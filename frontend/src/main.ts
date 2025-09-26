import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { VueQueryPlugin } from '@tanstack/vue-query'

// --- Vuetify ---
import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const utzLightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#F7FAFC', // Очень светлый серо-голубой фон
    surface: '#FFFFFF', // Белый фон для карточек
    primary: '#0055A5', // Основной корпоративный синий
    'primary-darken-1': '#003A75', // Более темный синий для hover/active состояний
    secondary: '#4A5568', // Темно-серый для второстепенных элементов
    accent: '#00A3E0', // Акцентный голубой
    error: '#E53E3E', // Красный
    info: '#00A3E0', // Можно использовать акцентный голубой
    success: '#38A169', // Зеленый
    warning: '#F58220', // Корпоративный оранжевый
  },
}

const utzDarkTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#1A202C', // Темно-сине-серый фон
    surface: '#2D3748', // Фон для карточек (чуть светлее)
    primary: '#00A3E0', // Акцентный голубой становится основным в темной теме
    'primary-darken-1': '#0082B3',
    secondary: '#A0AEC0', // Светло-серый для второстепенного текста
    accent: '#00A3E0',
    error: '#FC8181',
    info: '#63B3ED',
    success: '#68D391',
    warning: '#F6AD55',
  },
}

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'utzLightTheme',
    themes: {
      utzLightTheme,
      utzDarkTheme,
    },
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(VueQueryPlugin)

app.mount('#app')
