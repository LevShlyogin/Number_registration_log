<template>
  <v-container fluid class="pa-0">
    <!-- Форма поиска -->
    <v-card variant="outlined" class="mb-6">
      <v-card-title>Поиск оборудования</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="searchParams.station_object"
              label="Станция / Объект"
              clearable
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="searchParams.station_no" label="№ станционный" clearable />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="searchParams.label" label="Маркировка" clearable />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field v-model="searchParams.factory_no" label="№ заводской" clearable />
          </v-col>
          <v-col cols="12">
            <v-text-field v-model="searchParams.q" label="Поиск по всем полям" clearable />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="performSearch" :loading="isLoading" color="primary" variant="flat">
          <v-icon start icon="mdi-magnify"></v-icon>
          Поиск
        </v-btn>
        <v-btn @click="isCreateFormVisible = true" variant="tonal">
          <v-icon start icon="mdi-plus-circle-outline"></v-icon>
          Создать новый объект
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Результаты поиска -->
    <div id="search-results">
      <v-progress-linear v-if="isLoading" indeterminate color="primary"></v-progress-linear>
      <v-alert v-if="isError" type="error" variant="tonal" class="mb-4">
        Ошибка при поиске: {{ (error as Error).message }}
      </v-alert>

      <div v-if="results">
        <p v-if="results.length > 0" class="text-subtitle-1 mb-2">
          Найдено объектов: {{ results.length }}
        </p>
        <p v-else class="text-subtitle-1 mb-2 text-grey">
          Ничего не найдено. Попробуйте изменить параметры поиска или создайте новый объект.
        </p>

        <v-list lines="two">
          <v-list-item
            v-for="item in results"
            :key="item.id"
            @click="selectEquipment(item.id)"
            :active="selectedId === item.id"
            active-color="primary"
            rounded="lg"
            class="mb-2 border"
          >
            <template #prepend>
              <v-avatar color="primary">
                <v-icon icon="mdi-factory"></v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-bold"
              >{{ item.eq_type }} - {{ item.station_object || 'N/A' }}</v-list-item-title
            >
            <v-list-item-subtitle>
              Зав. №: {{ item.factory_no || '-' }} | Ст. №: {{ item.station_no || '-' }} |
              Маркировка: {{ item.label || '-' }}
            </v-list-item-subtitle>

            <template #append>
              <v-btn
                @click.stop="selectEquipment(item.id)"
                size="small"
                variant="tonal"
                color="primary"
              >
                Выбрать
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
      </div>
    </div>

    <!-- TODO: Форма создания (пока скрыта) -->
    <div v-if="isCreateFormVisible">
      <!-- Здесь будет компонент для создания нового оборудования -->
    </div>

    <!-- Навигация -->
    <div class="mt-6 d-flex justify-end">
      <v-btn
        @click="goNext"
        color="primary"
        size="large"
        :disabled="!wizardStore.hasSelectedEquipment"
      >
        Далее
        <v-icon end icon="mdi-arrow-right"></v-icon>
      </v-btn>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'
import { useEquipmentSearch, type SearchParams } from '@/composables/useEquipmentSearch'
import type { EquipmentOut } from '@/types/api'

const router = useRouter()
const wizardStore = useWizardStore()

const isCreateFormVisible = ref(false)
const selectedId = ref<number | null>(null)

// Реактивные параметры для формы поиска
const searchParams = reactive<SearchParams>({
  station_object: '',
  station_no: '',
  label: '',
  factory_no: '',
  order_no: '',
  q: '',
})

// Используем наш composable
const { results, isLoading, isError, error, search } = useEquipmentSearch(searchParams)

function performSearch() {
  selectedId.value = null // Сбрасываем выбор при новом поиске
  wizardStore.selectedEquipmentId = null
  search() // Запускаем поиск
}

function selectEquipment(id: number) {
  selectedId.value = id
  wizardStore.setEquipment(id)
}

function goNext() {
  if (wizardStore.selectedEquipmentId) {
    router.push({
      name: 'wizard-reserve',
      params: { equipmentId: wizardStore.selectedEquipmentId },
    })
  }
}
</script>
