<template>
  <div>
    <h3 class="text-h6 mb-4">Шаг 3: Назначение номеров</h3>
    <p class="text-body-1 mb-4">
      Сессия ID: <strong>{{ sessionId }}</strong>
    </p>
    <v-text-field label="Наименование документа"></v-text-field>
    <v-textarea label="Примечание"></v-textarea>
    <v-btn color="primary">Назначить следующий</v-btn>
    <div class="mt-4">
      <v-btn @click="goBack" class="mr-4" variant="outlined">Назад</v-btn>
      <v-btn @click="complete" color="success">Завершить</v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'

defineProps<{
  sessionId: string
}>()

const router = useRouter()
const wizardStore = useWizardStore()

function goBack() {
  router.back()
}

function complete() {
  wizardStore.reset()
  router.push({ name: 'reports' })
}
</script>
