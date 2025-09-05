<template>
  <v-card flat>
    <v-card-title class="text-h5 font-weight-bold"> Регистрация номеров документов </v-card-title>
    <v-card-subtitle>
      Пошаговый мастер для поиска оборудования и назначения номеров
    </v-card-subtitle>

    <v-card-text>
      <v-stepper :items="steps" v-model="currentStep" class="mb-5" alt-labels>
        <!-- Можно кастомизировать отображение шагов через слоты, если нужно -->
      </v-stepper>

      <!-- Здесь будут рендериться компоненты шагов -->
      <router-view />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const steps = ['Оборудование', 'Резерв', 'Назначение']
const currentStep = ref(1) // Шаги нумеруются с 1 в v-stepper

// Синхронизируем v-stepper с текущим роутом
watch(
  () => route.name,
  (routeName) => {
    switch (routeName) {
      case 'wizard-equipment':
        currentStep.value = 1
        break
      case 'wizard-reserve':
        currentStep.value = 2
        break
      case 'wizard-assign':
        currentStep.value = 3
        break
    }
  },
  { immediate: true },
)
</script>
