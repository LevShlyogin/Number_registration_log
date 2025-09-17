<template>
  <v-container fluid class="pa-0">
    <h3 class="text-h6 font-weight-medium mb-2">Шаг 2: Резервирование номеров</h3>
    <p class="text-body-1 mb-6">
      Оборудование ID: <strong>{{ equipmentId }}</strong>
    </p>

    <v-form @submit.prevent="handleReserve">
      <v-text-field
        v-model.number="quantity"
        type="number"
        label="Количество номеров для резервирования"
        :rules="[rules.required, rules.positive]"
        variant="filled"
        flat
        min="1"
        max="100"
        style="max-width: 400px"
        hide-details="auto"
        class="mb-4"
      />
      <v-btn type="submit" :loading="isLoading" color="primary" variant="flat">
        Резервировать
      </v-btn>
    </v-form>

    <v-alert v-if="isError" type="error" variant="tonal" class="mt-4">
      Ошибка при резервировании: {{ (error as Error).message }}
    </v-alert>

    <v-card v-if="result" variant="tonal" color="success" class="mt-6">
      <v-card-title>
        <v-icon start icon="mdi-check-circle"></v-icon>
        Успешно зарезервировано!
      </v-card-title>
      <v-card-text>
        <p class="font-weight-medium">
          ID сессии: <v-chip size="small">{{ result.session_id }}</v-chip>
        </p>
        <p class="mt-2 font-weight-medium">Номера:</p>
        <v-chip-group class="mt-1">
          <v-chip v-for="num in result.reserved_numbers" :key="num" label>
            {{ num }}
          </v-chip>
        </v-chip-group>
      </v-card-text>
    </v-card>

    <div class="mt-6 d-flex justify-space-between">
      <v-btn @click="goBack" variant="text">
        <v-icon start icon="mdi-arrow-left"></v-icon>
        Назад
      </v-btn>
      <v-btn
        @click="goNext"
        color="primary"
        size="large"
        :disabled="!wizardStore.hasActiveSession"
        variant="flat"
      >
        Далее
        <v-icon end icon="mdi-arrow-right"></v-icon>
      </v-btn>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'
import { useNumberReservation } from '@/composables/useNumberReservation'
import type { ReserveNumbersOut } from '@/types/api'

const props = defineProps<{
  equipmentId: string // Приходит из URL
}>()

const router = useRouter()
const wizardStore = useWizardStore()
const { reserve, isLoading, isError, error, result } = useNumberReservation()

const quantity = ref(1)
const rules = {
  required: (value: number) => !!value || 'Это поле обязательно.',
  positive: (value: number) => value > 0 || 'Количество должно быть больше нуля.',
}

function handleReserve() {
  reserve(
    {
      equipment_id: Number(props.equipmentId),
      quantity: quantity.value,
    },
    {
      onSuccess: (data: ReserveNumbersOut) => {
        // При успехе сохраняем данные в Pinia store
        wizardStore.setSession(data.session_id, data.reserved_numbers)
      },
      onError: () => {
        // Очищаем сессию в сторе, если резервирование не удалось
        wizardStore.currentSessionId = null
        wizardStore.reservedNumbers = []
      },
    },
  )
}

function goBack() {
  router.back()
}

function goNext() {
  if (wizardStore.currentSessionId) {
    router.push({
      name: 'wizard-assign',
      params: { sessionId: wizardStore.currentSessionId },
    })
  }
}
</script>
