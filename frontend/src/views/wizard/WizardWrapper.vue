<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="9">
        <v-card flat class="border">
          <v-card-title class="text-h5 font-weight-regular border-b pa-4 d-flex align-center">
            <v-icon icon="mdi-file-document-edit-outline" start color="grey-darken-1"></v-icon>
            Регистрация номеров документов
          </v-card-title>

          <div class="stepper-container pa-6">
            <div class="stepper-wrapper">
              <div
                v-for="(step, index) in steps"
                :key="step.value"
                class="stepper-item"
                :class="{
                  'stepper-item--active': currentStepIndex === step.value,
                  'stepper-item--complete': currentStepIndex > step.value,
                }"
              >
                <!-- Круг с номером -->
                <div class="stepper-circle">
                  <transition name="check" mode="out-in">
                    <v-icon
                      v-if="currentStepIndex > step.value"
                      icon="mdi-check"
                      size="small"
                      key="check"
                    />
                    <span v-else key="number">{{ step.value }}</span>
                  </transition>
                </div>

                <!-- Текст -->
                <div class="stepper-content">
                  <div class="stepper-title">{{ step.title }}</div>
                  <div class="stepper-subtitle">{{ step.subtitle }}</div>
                </div>

                <!-- Линия соединения -->
                <div v-if="index < steps.length - 1" class="stepper-line">
                  <div
                    class="stepper-line-progress"
                    :style="{ width: getLineProgress(step.value) }"
                  ></div>
                  <!-- Пульсирующая точка (видна только на активном шаге) -->
                  <div class="stepper-line-dot" v-if="currentStepIndex === step.value"></div>
                </div>
              </div>
            </div>
          </div>

          <v-divider></v-divider>

          <v-card-text class="pa-4 pa-sm-6">
            <router-view v-slot="{ Component }">
              <v-fade-transition mode="out-in">
                <component :is="Component" />
              </v-fade-transition>
            </router-view>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, onBeforeRouteLeave } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'

const route = useRoute()
const wizardStore = useWizardStore()

const currentStepIndex = ref(1)

const steps = [
  { value: 1, title: 'Оборудование', subtitle: 'Поиск или создание' },
  { value: 2, title: 'Резерв', subtitle: 'Получение номеров' },
  { value: 3, title: 'Назначение', subtitle: 'Привязка к документам' },
]

const getLineProgress = (stepValue: number) => {
  if (currentStepIndex.value > stepValue) {
    return '100%' // Если шаг пройден, линия заполнена полностью
  }
  // В остальных случаях (текущий или будущий шаг) линия пустая.
  return '0%'
}

watch(
  () => route.name,
  (routeName) => {
    switch (routeName) {
      case 'wizard-equipment':
        currentStepIndex.value = 1
        break
      case 'wizard-reserve':
        currentStepIndex.value = 2
        break
      case 'wizard-assign':
        currentStepIndex.value = 3
        break
    }
  },
  { immediate: true },
)

onBeforeRouteLeave((to, _from) => {
  if (
    !to.path.startsWith('/wizard') &&
    (wizardStore.hasSelectedEquipment || wizardStore.hasActiveSession)
  ) {
    const answer = window.confirm(
      'Вы уверены, что хотите покинуть мастер регистрации? Все несохраненные данные будут потеряны.',
    )
    if (!answer) return false
  }
  return true
})
</script>

<style scoped>
.stepper-container {
  background: rgba(var(--v-theme-surface-variant), 0.04);
}

.stepper-wrapper {
  display: flex;
  align-items: flex-start; /* Выравнивание по верху для консистентности */
  justify-content: center;
  position: relative;
}

.stepper-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
  max-width: 200px;
}

/* Круг с номером */
.stepper-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-on-surface), 0.08);
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-weight: 500;
  position: relative;
  z-index: 2;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 12px;
}

.stepper-item--active .stepper-circle {
  background: rgb(var(--v-theme-primary));
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary-rgb), 0.3);
}

.stepper-item--complete .stepper-circle {
  background: rgb(var(--v-theme-primary));
  color: white;
}

/* Контент */
.stepper-content {
  text-align: center;
}

.stepper-title {
  font-weight: 500;
  color: rgba(var(--v-theme-on-surface), 0.87);
  margin-bottom: 4px;
  transition: all 0.3s ease;
}

.stepper-subtitle {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  transition: all 0.3s ease;
}

.stepper-item--active .stepper-title {
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}

.stepper-item--active .stepper-subtitle {
  color: rgba(var(--v-theme-primary-rgb), 0.8);
}

/* Линия соединения */
.stepper-line {
  position: absolute;
  top: 20px; /* Вертикальное выравнивание по центру круга (40px / 2) */
  left: 50%;
  width: 100%;
  height: 2px;
  background: rgba(var(--v-theme-on-surface), 0.12);
  z-index: 1;
}

.stepper-line-progress {
  height: 100%;
  background: rgb(var(--v-theme-primary));
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Пульсирующая точка */
.stepper-line-dot {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgb(var(--v-theme-primary));
  animation: pulse 2s infinite;
  z-index: 3;
}

/* Анимации */
.check-enter-active,
.check-leave-active {
  transition: all 0.3s ease;
}

.check-enter-from {
  opacity: 0;
  transform: scale(0.5) rotate(-90deg);
}

.check-leave-to {
  opacity: 0;
  transform: scale(0.5) rotate(90deg);
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(var(--v-theme-primary-rgb), 0.4);
  }
  70% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 10px rgba(var(--v-theme-primary-rgb), 0);
  }
  100% {
    transform: translate(-50%, -50%) scale(1);
    box-shadow: 0 0 0 0 rgba(var(--v-theme-primary-rgb), 0);
  }
}

/* Адаптивность */
@media (max-width: 600px) {
  .stepper-wrapper {
    flex-direction: column;
    gap: 24px;
    align-items: flex-start;
  }

  .stepper-item {
    flex-direction: row;
    max-width: 100%;
    width: 100%;
  }

  .stepper-circle {
    margin-bottom: 0;
    margin-right: 16px;
  }

  .stepper-content {
    text-align: left;
    flex: 1;
  }

  .stepper-line {
    display: none;
  }
}
</style>
