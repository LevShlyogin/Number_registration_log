<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title class="app-title">
        <v-icon icon="mdi-notebook-edit-outline" class="mr-2"></v-icon>
        Журнал регистрации УТЗ
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <div v-if="user.username" class="user-info mr-4">
        Пользователь: <strong>{{ user.username }}</strong>
        <v-chip v-if="user.isAdmin" size="small" color="amber" class="ml-2">Админ</v-chip>
      </div>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>

    <v-footer app class="text-center d-flex flex-column pa-0">
      <div class="bg-primary d-flex w-100 align-center px-4">
        <!-- Можно добавить иконки соцсетей или другую информацию -->
        <v-spacer></v-spacer>
      </div>
      <div class="px-4 py-2 bg-black text-center w-100">
        © {{ new Date().getFullYear() }} — <strong>FastAPI + Vue.js</strong>
      </div>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Заглушка для информации о пользователе
// В реальном приложении это будет приходить из Pinia-стора или composable-функции
const user = ref({
  username: 'yuaalekseeva',
  isAdmin: true,
})

// onMounted(() => {
//   // Здесь будет логика для получения X-User и установки в Pinia store
// });
</script>

<style scoped>
.app-title {
  cursor: pointer;
  font-weight: 600;
}
.user-info {
  font-size: 0.9rem;
}
</style>
