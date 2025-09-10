import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// --- Vue Query ---
import { VueQueryPlugin } from '@tanstack/vue-query'

// --- Vuetify ---
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light', // Или 'dark'
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#1976D2', // Синий
          secondary: '#424242', // Темно-серый
          accent: '#82B1FF', // Светло-синий
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
      dark: {
        dark: true,
        colors: {
          primary: '#2196F3',
          // ... можно определить цвета и для темной темы
        },
      },
    },
  },
})
// --- Конец Vuetify ---

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(VueQueryPlugin)

app.mount('#app')
