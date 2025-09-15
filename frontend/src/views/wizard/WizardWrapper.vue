<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card flat class="border">
          <v-card-title class="text-h5 font-weight-bold border-b">
            <v-icon icon="mdi-file-document-edit-outline" start></v-icon>
            Регистрация номеров документов
          </v-card-title>
          <v-stepper v-model="currentStep" :items="steps" alt-labels hide-actions flat> </v-stepper>
          <v-divider></v-divider>
          <v-card-text class="pa-sm-6">
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

const steps = ['Оборудование', 'Резерв', 'Назначение']
const currentStep = ref(1)

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

onBeforeRouteLeave((to, from) => {
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
