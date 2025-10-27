<template>
  <v-container fluid class="pa-0">
    <h3 class="text-h6 font-weight-medium mb-2">Шаг 2: Резервирование номеров</h3>
    <p class="text-body-1 mb-6">
      Выбрано оборудование ID: <strong>{{ equipmentId }}</strong>
    </p>

    <v-row>
      <!-- Основная форма резервирования -->
      <v-col cols="12" :md="auth.isAdmin ? 6 : 12">
        <v-sheet class="pa-4 border rounded-lg" height="100%">
          <h4 class="text-subtitle-1 font-weight-medium mb-4">Обычный резерв</h4>
          <v-form @submit.prevent="handleReserve">
            <v-text-field
              v-model.number="quantity"
              type="number"
              label="Количество номеров"
              :rules="[rules.required, rules.positive]"
              variant="filled"
              flat
              hide-details="auto"
              min="1"
              max="100"
              class="mb-4"
            />
            <v-btn type="submit" :loading="isLoading" color="primary" variant="flat">
              Резервировать
            </v-btn>
          </v-form>
        </v-sheet>
      </v-col>

      <!-- Блок "Золотые номера" для админа -->
      <v-col v-if="auth.isAdmin" cols="12" md="6">
        <v-sheet class="pa-4 border rounded-lg" height="100%">
          <h4 class="text-subtitle-1 font-weight-medium mb-4 d-flex align-center">
            <v-icon start icon="mdi-star-circle-outline" color="amber"></v-icon>
            Резерв "золотых" номеров
          </h4>
          <v-form @submit.prevent="handleReserveGolden">
            <v-text-field
              v-model="goldenNumbersInput"
              label="Номера через запятую"
              placeholder="NNNN00, NNNN00, NNNN00"
              variant="filled"
              flat
              hide-details="auto"
              class="mb-4"
            ></v-text-field>
            <v-btn type="submit" :loading="isReservingSpecific" color="amber" variant="flat">
              Зарезервировать указанные
            </v-btn>
          </v-form>
        </v-sheet>
      </v-col>
    </v-row>

    <!-- Карточка с результатом -->
    <v-expand-transition>
      <v-card v-if="wizardStore.hasActiveSession" variant="tonal" color="success" class="mt-6">
        <v-card-title>
          <v-icon start icon="mdi-check-circle"></v-icon>
          Успешно зарезервировано!
        </v-card-title>
        <v-card-text>
          <!-- Используем данные ИЗ СТОРА -->
          <p class="mt-2 font-weight-medium">
            Всего зарезервировано: {{ wizardStore.reservedNumbers.length }}
          </p>
          <v-sheet max-height="150" class="scrollable-chip-group pa-2 mt-1" color="transparent">
            <v-chip-group>
              <v-chip v-for="num in wizardStore.reservedNumbers" :key="num" label>
                {{ num }}
              </v-chip>
            </v-chip-group>
          </v-sheet>
        </v-card-text>
      </v-card>
    </v-expand-transition>

    <!-- Навигация -->
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
import { useAuthStore } from '@/stores/auth'
import { useNumberReservation } from '@/composables/useNumberReservation'
import { useNotifier } from '@/composables/useNotifier'
import type { ReserveNumbersOut } from '@/types/api'
import { AxiosError } from 'axios'

const props = defineProps<{ equipmentId: string }>()

const router = useRouter()
const wizardStore = useWizardStore()
const auth = useAuthStore()
const notifier = useNotifier()
const { reserve, isLoading, reserveSpecific, isReservingSpecific } = useNumberReservation()

const quantity = ref(1)
const goldenNumbersInput = ref('')
const rules = {
  required: (value: number) => !!value || 'Это поле обязательно.',
  positive: (value: number) => value > 0 || 'Количество должно быть больше нуля.',
}

function handleApiError(error: unknown) {
  let message = 'Произошла неизвестная ошибка'
  if (error instanceof AxiosError && error.response?.data?.detail) {
    message = error.response.data.detail
  } else if (error instanceof Error) {
    message = error.message
  }
  notifier.error(message)
}

function handleReserve() {
  if (!quantity.value || quantity.value <= 0) {
    notifier.warning('Введите корректное количество номеров (больше нуля).')
    return
  }

  reserve(
    {
      equipment_id: Number(props.equipmentId),
      requested_count: quantity.value,
    },
    {
      onSuccess: (data: ReserveNumbersOut) => {
        wizardStore.setSession(data.session_id, [
          ...wizardStore.reservedNumbers,
          ...data.reserved_numbers,
        ])
        notifier.success(`Успешно зарезервировано ${data.reserved_numbers.length} номер(а)!`)
      },
      onError: (e) => {
        handleApiError(e)
      },
    },
  )
}

function handleReserveGolden() {
  const numbers = goldenNumbersInput.value
    .split(',')
    .map((n) => parseInt(n.trim(), 10))
    .filter((n) => !isNaN(n) && n > 0)

  if (numbers.length === 0) {
    notifier.warning('Введите корректные числовые номера через запятую.')
    return
  }

  reserveSpecific(
    {
      equipment_id: Number(props.equipmentId),
      numbers: numbers,
    },
    {
      onSuccess: (data: ReserveNumbersOut) => {
        wizardStore.setSession(data.session_id, [
          ...wizardStore.reservedNumbers,
          ...data.reserved_numbers,
        ])
        notifier.success(
          `Успешно зарезервировано ${data.reserved_numbers.length} "золотых" номер(а)!`,
        )
        goldenNumbersInput.value = ''
      },
      onError: (e) => {
        handleApiError(e)
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

<style scoped>
.scrollable-chip-group {
  max-height: 150px;
  overflow-y: auto;
}
</style>
