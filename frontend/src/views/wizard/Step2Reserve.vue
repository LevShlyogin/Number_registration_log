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
            <!-- ИЗМЕНЕНИЕ ЗДЕСЬ: используем 'anyLoading' -->
            <v-btn type="submit" :loading="anyLoading" color="primary" variant="flat">
              <v-icon start>{{
                wizardStore.hasActiveSession ? 'mdi-plus' : 'mdi-lock-outline'
              }}</v-icon>
              {{ wizardStore.hasActiveSession ? 'Добавить' : 'Резервировать' }}
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
              placeholder="Например: 1200, 1300, 2500"
              variant="filled"
              flat
              hide-details="auto"
              class="mb-4"
            ></v-text-field>
            <!-- ИЗМЕНЕНИЕ ЗДЕСЬ: используем 'anyLoading' -->
            <v-btn type="submit" :loading="anyLoading" color="amber" variant="flat">
              <v-icon start>{{
                wizardStore.hasActiveSession ? 'mdi-plus' : 'mdi-lock-outline'
              }}</v-icon>
              {{ wizardStore.hasActiveSession ? 'Добавить' : 'Резервировать' }}
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
          Текущий пул номеров
        </v-card-title>
        <v-card-text>
          <p class="mt-2 font-weight-medium">
            Всего зарезервировано: {{ wizardStore.reservedNumbers.length }}
          </p>
          <v-sheet max-height="150" class="scrollable-chip-group pa-2 mt-1" color="transparent">
            <v-chip-group>
              <v-chip v-for="num in sortedReservedNumbers" :key="num" label>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'
import { useAuthStore } from '@/stores/auth'
import { useNumberReservation } from '@/composables/useNumberReservation'
import { useNotifier } from '@/composables/useNotifier'
import { AxiosError } from 'axios'

const props = defineProps<{ equipmentId: string }>()

const router = useRouter()
const wizardStore = useWizardStore()
const auth = useAuthStore()
const notifier = useNotifier()
const { reserve, isLoading, reserveSpecific, isReservingSpecific, addNumbers, isAdding } =
  useNumberReservation()

const quantity = ref(1)
const goldenNumbersInput = ref('')
const anyLoading = computed(() => isLoading.value || isReservingSpecific.value || isAdding.value)

const sortedReservedNumbers = computed(() => [...wizardStore.reservedNumbers].sort((a, b) => a - b))

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
  if (anyLoading.value) return

  if (wizardStore.hasActiveSession) {
    addNumbers(
      {
        sessionId: wizardStore.currentSessionId!,
        payload: { requested_count: quantity.value },
      },
      {
        onSuccess: (newNumbers) => {
          wizardStore.reservedNumbers.push(...newNumbers)
          notifier.success(`Добавлено ${newNumbers.length} номер(а)`)
        },
        onError: handleApiError,
      },
    )
  } else {
    reserve(
      {
        equipment_id: Number(props.equipmentId),
        requested_count: quantity.value,
      },
      {
        onSuccess: (data) => {
          wizardStore.setSession(data.session_id, data.reserved_numbers)
          notifier.success(`Успешно зарезервировано ${data.reserved_numbers.length} номер(а)`)
        },
        onError: handleApiError,
      },
    )
  }
}

function handleReserveGolden() {
  if (anyLoading.value) return
  const numbers = goldenNumbersInput.value
    .split(',')
    .map((n) => parseInt(n.trim(), 10))
    .filter(Boolean)
  if (numbers.length === 0) {
    notifier.warning('Введите корректные номера.')
    return
  }

  if (wizardStore.hasActiveSession) {
    addNumbers(
      {
        sessionId: wizardStore.currentSessionId!,
        payload: { numbers },
      },
      {
        onSuccess: (newNumbers) => {
          wizardStore.reservedNumbers.push(...newNumbers)
          goldenNumbersInput.value = ''
          notifier.success(`Добавлено ${newNumbers.length} "золотых" номер(а)`)
        },
        onError: handleApiError,
      },
    )
  } else {
    reserveSpecific(
      {
        equipment_id: Number(props.equipmentId),
        numbers,
      },
      {
        onSuccess: (data) => {
          wizardStore.setSession(data.session_id, data.reserved_numbers)
          goldenNumbersInput.value = ''
          notifier.success(`Зарезервировано ${data.reserved_numbers.length} "золотых" номер(а)`)
        },
        onError: handleApiError,
      },
    )
  }
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
