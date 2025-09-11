<template>
  <v-container fluid class="pa-0">
    <h3 class="text-h6 mb-2">Шаг 3: Назначение номеров</h3>
    <p class="text-body-1 mb-4 text-grey">
      Сессия ID: <strong>{{ sessionId }}</strong>
    </p>

    <v-row>
      <!-- Левая колонка: форма назначения -->
      <v-col cols="12" md="5">
        <v-card variant="outlined">
          <v-card-title> Форма назначения </v-card-title>
          <v-card-text>
            <v-form ref="formRef" @submit.prevent="handleAssign">
              <p class="text-subtitle-1 mb-2">
                Свободно номеров: <strong class="text-success">{{ freeNumbers.length }}</strong>
              </p>
              <p class="text-subtitle-2 text-grey mb-4">
                Следующий номер для назначения:
                <strong v-if="nextFreeNumber" class="text-primary">{{ nextFreeNumber }}</strong>
                <em v-else>нет</em>
              </p>
              <v-text-field
                v-model="formData.doc_name"
                label="Наименование документа"
                :rules="[rules.required]"
                :disabled="isAssigning || freeNumbers.length === 0"
                class="mb-2"
                hide-details="auto"
              ></v-text-field>
              <v-textarea
                v-model="formData.notes"
                label="Примечание"
                rows="3"
                :disabled="isAssigning || freeNumbers.length === 0"
                hide-details="auto"
              ></v-textarea>

              <v-btn
                type="submit"
                :loading="isAssigning"
                :disabled="freeNumbers.length === 0"
                color="primary"
                variant="flat"
                block
                class="mt-4"
              >
                <v-icon start icon="mdi-plus-box"></v-icon>
                Назначить следующий
              </v-btn>

              <v-alert v-if="isErrorAssigning" type="error" variant="tonal" class="mt-4">
                {{ (errorAssigning as Error).message }}
              </v-alert>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Правая колонка: списки номеров -->
      <v-col cols="12" md="7">
        <v-row>
          <!-- Свободные номера -->
          <v-col cols="12" sm="6">
            <v-card variant="outlined" height="100%">
              <v-card-title>Свободные номера</v-card-title>
              <v-card-text>
                <v-chip v-if="freeNumbers.length === 0" color="grey" size="small"
                  >Нет свободных номеров</v-chip
                >
                <v-chip-group v-else>
                  <v-chip v-for="num in freeNumbers" :key="num" size="small">
                    {{ num }}
                  </v-chip>
                </v-chip-group>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Назначенные номера -->
          <v-col cols="12" sm="6">
            <v-card variant="outlined" height="100%">
              <v-card-title>Назначенные номера</v-card-title>
              <v-progress-linear v-if="isLoadingAssigned" indeterminate></v-progress-linear>
              <v-card-text>
                <v-list v-if="assignedNumbers && assignedNumbers.length > 0" density="compact">
                  <v-list-item
                    v-for="item in assignedNumbers"
                    :key="item.doc_no"
                    :title="String(item.doc_no)"
                    :subtitle="item.doc_name"
                  ></v-list-item>
                </v-list>
                <v-chip v-else color="grey" size="small">Еще нет назначенных номеров</v-chip>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- Навигация -->
    <div class="mt-6 d-flex justify-space-between align-center">
      <v-btn @click="goBack" variant="outlined">
        <v-icon start icon="mdi-arrow-left"></v-icon>
        Назад
      </v-btn>
      <v-alert
        v-if="freeNumbers.length === 0 && wizardStore.hasActiveSession"
        type="warning"
        variant="tonal"
        density="compact"
        class="text-caption"
      >
        Все зарезервированные номера назначены.
      </v-alert>
      <v-btn @click="complete" color="success" size="large">
        <v-icon start icon="mdi-check-all"></v-icon>
        Завершить
      </v-btn>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'
import { useNumberAssignment } from '@/composables/useNumberAssignment'
import type { AssignNumberIn } from '@/types/api'

const props = defineProps<{
  sessionId: string
}>()

const router = useRouter()
const wizardStore = useWizardStore()
const {
  assignedNumbers,
  isLoadingAssigned,
  isErrorAssigning,
  errorAssigning,
  assignNumber,
  isAssigning,
} = useNumberAssignment(props.sessionId)

const formRef = ref<any>(null)
const formData = reactive<Omit<AssignNumberIn, 'session_id'>>({
  doc_name: '',
  notes: '',
})
const rules = {
  required: (value: string) => !!value || 'Это поле обязательно.',
}

// Вычисляем список свободных номеров
const freeNumbers = computed(() => {
  const assignedSet = new Set(assignedNumbers.value?.map((item) => item.doc_no) ?? [])
  return wizardStore.reservedNumbers.filter((num) => !assignedSet.has(num))
})

// Получаем следующий свободный номер для отображения
const nextFreeNumber = computed(() => {
  return freeNumbers.value.length > 0 ? freeNumbers.value[0] : null
})

async function handleAssign() {
  const { valid } = await formRef.value.validate()
  if (valid && wizardStore.currentSessionId) {
    assignNumber(
      {
        session_id: wizardStore.currentSessionId,
        doc_name: formData.doc_name,
        notes: formData.notes,
      },
      {
        onSuccess: () => {
          // После успеха сбрасываем поля формы для следующего назначения
          formRef.value.reset()
        },
      },
    )
  }
}

function goBack() {
  router.back()
}

function complete() {
  wizardStore.reset() // Очищаем состояние визарда
  router.push({ name: 'reports' }) // Переходим на страницу отчетов
}
</script>
