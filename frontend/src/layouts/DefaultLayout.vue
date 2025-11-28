<template>
  <v-app>
    <!-- AppBar (Header) -->
    <v-app-bar app flat border color="surface">
      <v-container class="d-flex align-center px-4 px-sm-6" fluid>
        <!-- Лого и Название -->
        <v-toolbar-title class="app-title d-flex align-center" @click="router.push('/')">
          <v-avatar class="mr-3">
            <v-img src="/logo.png" alt="УТЗ Лого"></v-img>
          </v-avatar>
          <span class="font-weight-bold d-none d-sm-inline">Журнал регистрации</span>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <!-- Навигационные ссылки Десктоп -->
        <div class="d-none d-md-flex">
          <template v-for="link in navLinks" :key="link.to">
            <v-btn
              v-if="!link.adminOnly || auth.isAdmin"
              :to="link.to"
              variant="text"
              class="nav-link"
              color="secondary"
            >
              <v-icon :icon="link.icon" start></v-icon>
              {{ link.label }}
            </v-btn>
          </template>
        </div>

        <!-- Кнопка темы -->
        <theme-toggle-button />

        <!-- Информация о пользователе и Выход -->
        <div v-if="auth.user" class="user-info ml-3 pl-3 border-s">
          <v-avatar size="32" class="mr-2">
            <v-icon icon="mdi-account-circle" color="secondary"></v-icon>
          </v-avatar>
          <div class="d-none d-lg-block">
            <div class="username">{{ auth.fullName }}</div>
            <div class="login">{{ auth.user.username }}</div>
          </div>

          <!-- Кнопка выхода Десктоп -->
          <v-tooltip text="Выйти" location="bottom">
            <template #activator="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-logout"
                variant="text"
                size="small"
                color="medium-emphasis"
                class="ml-1"
                @click="auth.logout()"
              ></v-btn>
            </template>
          </v-tooltip>
        </div>

        <!-- Мобильное меню (бургер) -->
        <v-app-bar-nav-icon
          class="d-md-none ml-2"
          @click.stop="isNavDrawerOpen = !isNavDrawerOpen"
        ></v-app-bar-nav-icon>
      </v-container>

      <!-- Глобальный индикатор загрузки -->
      <v-progress-linear
        v-if="isFetching > 0"
        indeterminate
        absolute
        bottom
        color="accent"
      ></v-progress-linear>
    </v-app-bar>

    <!-- Мобильная навигация (Drawer) -->
    <v-navigation-drawer v-model="isNavDrawerOpen" temporary location="right">
      <div v-if="auth.user" class="pa-4 border-b">
        <div class="text-subtitle-1 font-weight-bold">{{ auth.fullName }}</div>
        <div class="text-caption text-medium-emphasis">{{ auth.user.username }}</div>
      </div>

      <v-list>
        <template v-for="link in navLinks" :key="link.to">
          <v-list-item
            v-if="!link.adminOnly || auth.isAdmin"
            :to="link.to"
            :prepend-icon="link.icon"
            :title="link.label"
            @click="isNavDrawerOpen = false"
          ></v-list-item>
        </template>

        <v-divider class="my-2"></v-divider>

        <!-- Кнопка ВЫХОД (Мобилка) -->
        <v-list-item
          prepend-icon="mdi-logout"
          title="Выйти"
          color="error"
          @click="handleLogout"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Основной контент -->
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>

    <!-- Уведомления -->
    <v-snackbar
      v-model="notifier.show.value"
      :color="notifier.color.value"
      :timeout="notifier.timeout.value"
      location="bottom right"
      multi-line
    >
      {{ notifier.text.value }}
      <template #actions>
        <v-btn variant="text" @click="notifier.show.value = false"> Закрыть </v-btn>
      </template>
    </v-snackbar>

    <!-- Footer -->
    <v-footer app class="justify-center" height="40" color="surface" border>
      <div class="text-caption text-disabled">
        © {{ new Date().getFullYear() }} — АО «Уральский турбинный завод»
      </div>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggleButton from '@/components/ThemeToggleButton.vue'
import { useAuthStore } from '@/stores/auth'
import { useIsFetching } from '@tanstack/vue-query'
import { useNotifier } from '@/composables/useNotifier'

const router = useRouter()
const auth = useAuthStore()
const isNavDrawerOpen = ref(false)
const notifier = useNotifier()

const navLinks = [
  { to: '/wizard', label: 'Регистрация', icon: 'mdi-file-document-edit-outline' },
  { to: '/reports', label: 'Отчеты', icon: 'mdi-chart-bar' },
  { to: '/admin', label: 'Админка', icon: 'mdi-shield-crown-outline', adminOnly: true },
]

const isFetching = useIsFetching()

function handleLogout() {
  auth.logout()
  isNavDrawerOpen.value = false
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    auth.fetchUser()
  }
})
</script>

<style scoped>
.app-title {
  cursor: pointer;
}
.user-info {
  display: flex;
  align-items: center;
}
.username {
  font-weight: 500;
  font-size: 0.9rem;
  line-height: 1.1;
}
.login {
  font-size: 0.8rem;
  color: grey;
  line-height: 1.1;
}
</style>
