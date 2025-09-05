<template>
  <div>
    <h3 class="text-h6 mb-4">Шаг 1: Поиск или создание оборудования</h3>
    <v-text-field label="Станция / Объект" placeholder="Мосэнерго ТЭЦ-23"></v-text-field>
    <v-text-field label="№ заводской" placeholder="12345"></v-text-field>
    <v-btn color="primary" class="mr-4">Поиск</v-btn>
    <v-btn variant="tonal">Создать новый</v-btn>
    <div class="mt-4">
      <v-alert type="info" variant="outlined" class="mb-4">
        Здесь будут отображаться результаты поиска.
      </v-alert>
      <v-btn @click="selectAndGoNext" color="primary" disabled>Далее</v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'

const router = useRouter()
const wizardStore = useWizardStore()

function selectAndGoNext() {
  const fakeEquipmentId = 123 // Заглушка
  wizardStore.setEquipment(fakeEquipmentId)
  router.push({ name: 'wizard-reserve', params: { equipmentId: fakeEquipmentId } })
}
</script>
