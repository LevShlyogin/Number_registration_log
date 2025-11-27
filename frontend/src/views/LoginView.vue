<template>
  <v-app>
    <v-main class="login-background">
      <v-container class="fill-height" fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="5" lg="4" xl="3">
            <!-- Логотип и заголовок -->
            <div class="text-center mb-8">
              <v-avatar size="80" class="mb-4 elevation-3 bg-white pa-2">
                <v-img src="/logo.png" alt="УТЗ Лого" contain></v-img>
              </v-avatar>
              <h1 class="text-h4 font-weight-bold text-primary">УТЗ</h1>
              <div class="text-subtitle-1 text-medium-emphasis mt-1">
                Единая система авторизации
              </div>
            </div>

            <!-- Карточка входа -->
            <v-card class="rounded-lg elevation-4 pa-4" :loading="loading">
              <template #loader="{ isActive }">
                <v-progress-linear
                  :active="isActive"
                  color="primary"
                  height="4"
                  indeterminate
                ></v-progress-linear>
              </template>

              <v-card-title class="text-center pt-4 pb-2">
                <span class="text-h6 font-weight-medium">Вход в систему</span>
              </v-card-title>

              <v-card-text>
                <p class="text-body-2 text-center text-medium-emphasis mb-6">
                  Журнал регистрации номеров КД
                </p>

                <v-form @submit.prevent="handleLogin" ref="formRef">
                  <v-text-field
                    v-model="username"
                    label="Имя пользователя (AD)"
                    placeholder="ivanov"
                    prepend-inner-icon="mdi-account-outline"
                    variant="outlined"
                    color="primary"
                    density="comfortable"
                    class="mb-2"
                    autofocus
                    :rules="[rules.required]"
                    :disabled="loading"
                  ></v-text-field>

                  <v-text-field
                    v-model="password"
                    label="Пароль"
                    placeholder="••••••••"
                    prepend-inner-icon="mdi-lock-outline"
                    :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showPassword = !showPassword"
                    :type="showPassword ? 'text' : 'password'"
                    variant="outlined"
                    color="primary"
                    density="comfortable"
                    :rules="[rules.required]"
                    :disabled="loading"
                  ></v-text-field>

                  <v-expand-transition>
                    <div v-if="errorMsg">
                      <v-alert
                        type="error"
                        variant="tonal"
                        density="compact"
                        class="mt-4 mb-2"
                        closable
                        @click:close="errorMsg = ''"
                      >
                        {{ errorMsg }}
                      </v-alert>
                    </div>
                  </v-expand-transition>

                  <v-btn
                    type="submit"
                    color="primary"
                    size="large"
                    block
                    variant="flat"
                    class="mt-6 font-weight-bold"
                    :loading="loading"
                  >
                    Войти
                  </v-btn>
                </v-form>
              </v-card-text>

              <v-card-text class="text-center pt-2 pb-4">
                <div class="text-caption text-disabled">
                  Используйте вашу доменную учетную запись
                </div>
              </v-card-text>
            </v-card>

            <!-- Футер внутри контейнера центрирования -->
            <div class="text-center mt-8 text-caption text-disabled">
              © {{ new Date().getFullYear() }} — АО «Уральский турбинный завод»
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const errorMsg = ref('')

const authStore = useAuthStore()
const router = useRouter()

const rules = {
  required: (v: string) => !!v || 'Обязательное поле',
}

async function handleLogin() {
  if (!username.value || !password.value) return

  loading.value = true
  errorMsg.value = ''

  try {
    await authStore.login(username.value, password.value)
    await router.push('/')
  } catch (error: any) {
    if (error.response?.status === 401) {
      errorMsg.value = 'Неверное имя пользователя или пароль'
    } else if (error.code === 'ERR_NETWORK') {
      errorMsg.value = 'Сервер авторизации недоступен'
    } else {
      errorMsg.value = 'Произошла ошибка при входе'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-background {
  min-height: 100vh;
}
</style>
