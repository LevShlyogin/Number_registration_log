<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card flat class="border">
          <v-card-title class="text-h5 font-weight-bold border-b">
            <v-icon icon="mdi-file-document-edit-outline" start></v-icon>
            Регистрация номеров документов
          </v-card-title>

          <v-stepper v-model="currentStep" :items="steps" alt-labels hide-actions flat>
            <!-- alt-labels делает шаги с текстом под иконкой, hide-actions убирает дефолтные кнопки -->
          </v-stepper>

          <v-divider></v-divider>

          <v-card-text>
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
import { onBeforeRouteLeave } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'

const wizardStore = useWizardStore()

onBeforeRouteLeave((to, from) => {
  // Если уходим не на следующую/предыдущую страницу визарда, и есть активное состояние
  if (!to.path.startsWith('/wizard') && (wizardStore.hasSelectedEquipment || wizardStore.hasActiveSession)) {
    const answer = window.confirm(
      'Вы уверены, что хотите покинуть мастер регистрации? Все несохраненные данные будут потеряны.'
    )
    if (!answer) return false // Отменяем навигацию
  }
})
</script>