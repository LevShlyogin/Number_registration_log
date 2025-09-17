<template>
  <v-app>
    <!-- AppBar (Header) -->
    <v-app-bar app flat border color="surface">
      <v-container class="d-flex align-center pa-0" fluid>
        <!-- Лого и Название -->
        <v-toolbar-title class="app-title d-flex align-center" @click="router.push('/')">
          <v-avatar class="mr-3">
            <v-img src="/logo.png" alt="УТЗ Лого"></v-img>
          </v-avatar>
          <span class="font-weight-bold d-none d-sm-inline">Журнал регистрации</span>
        </v-toolbar-title>

        <v-spacer></v-spacer>

        <!-- Навигационные ссылки -->
        <div class="d-none d-md-flex">
          <v-btn
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            variant="text"
            class="nav-link"
            color="secondary"
          >
            <v-icon :icon="link.icon" start></v-icon>
            {{ link.label }}
          </v-btn>
        </div>

        <!-- Кнопка темы и информация о пользователе -->
        <theme-toggle-button />
        <div v-if="auth.user" class="user-info ml-3 pl-3 border-s">
          <v-avatar size="32" class="mr-2">
            <v-icon icon="mdi-account-circle" color="secondary"></v-icon>
          </v-avatar>
          <div class="d-none d-lg-block">
            <div class="username">{{ auth.user.fullName }}</div>
            <div class="login">{{ auth.user.login }}</div>
          </div>
        </div>

        <!-- Мобильное меню (бургер) -->
        <v-app-bar-nav-icon
          class="d-md-none"
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
      </v-list>
    </v-navigation-drawer>

    <!-- Основной контент -->
    <v-main>
      <v-container>
        <router-view />
      </v-container>
    </v-main>

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

const router = useRouter()
const auth = useAuthStore()
const isNavDrawerOpen = ref(false)

const navLinks = [
  { to: '/wizard', label: 'Регистрация', icon: 'mdi-file-document-edit-outline' },
  { to: '/reports', label: 'Отчеты', icon: 'mdi-chart-bar' },
  { to: '/admin', label: 'Админка', icon: 'mdi-shield-crown-outline', adminOnly: true },
]

const isFetching = useIsFetching()

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
