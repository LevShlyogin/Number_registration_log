<template>
  <div>
    <h3 class="text-h6 mb-4">Шаг 2: Резервирование номеров</h3>
    <p class="text-body-1 mb-4">
      Оборудование ID: <strong>{{ equipmentId }}</strong>
    </p>
    <v-text-field
      type="number"
      label="Количество номеров"
      min="1"
      max="100"
      model-value="1"
    ></v-text-field>
    <v-btn color="primary">Резервировать</v-btn>
    <div class="mt-4">
      <v-btn @click="goBack" class="mr-4" variant="outlined">Назад</v-btn>
      <v-btn @click="goNext" color="primary" disabled>Далее</v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'

// Получаем пропс, переданный из роутера
defineProps<{
  equipmentId: string
}>()

const router = useRouter()
const wizardStore = useWizardStore()

function goBack() {
  router.back()
}

function goNext() {
  const fakeSessionId = 'xyz-abc-123' // Заглушка
  wizardStore.setSession(fakeSessionId, [1001, 1002])
  router.push({ name: 'wizard-assign', params: { sessionId: fakeSessionId } })
}
</script>
