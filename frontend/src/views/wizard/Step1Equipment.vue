<template>
  <v-container fluid class="pa-0">
    <!-- Форма поиска -->
    <v-card variant="outlined" class="mb-6">
      <v-card-title>
        <v-icon start icon="mdi-magnify"></v-icon>
        Поиск оборудования
      </v-card-title>
      <v-card-text>
        <!-- Форма теперь использует v-form для валидации, если нужно -->
        <v-form @submit.prevent="performSearch">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formParams.station_object"
                label="Станция / Объект"
                clearable
                hide-details="auto"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formParams.station_no"
                label="№ станционный"
                clearable
                hide-details="auto"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formParams.label"
                label="Маркировка"
                clearable
                hide-details="auto"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formParams.factory_no"
                label="№ заводской"
                clearable
                hide-details="auto"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="formParams.q"
                label="Поиск по всем полям"
                clearable
                hide-details="auto"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="performSearch" :loading="isLoading" color="primary" variant="flat">
          Поиск
        </v-btn>
        <v-btn @click="showCreateForm" variant="tonal"> Создать новый объект </v-btn>
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
        <p v-else class="text-subtitle-1 mb-2 text-grey">Ничего не найдено.</p>

        <v-list lines="two" select-strategy="single-independent">
          <v-list-item
            v-for="item in results"
            :key="item.id"
            @click="selectEquipment(item.id)"
            :value="item.id"
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
          </v-list-item>
        </v-list>
      </div>
    </div>

    <!-- Модальное окно для создания нового оборудования -->
    <equipment-create-dialog v-model="isCreateDialogVisible" @success="onEquipmentCreated" />

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
import EquipmentCreateDialog from '@/components/wizard/EquipmentCreateDialog.vue' // Наш новый компонент

const router = useRouter()
const wizardStore = useWizardStore()

const isCreateDialogVisible = ref(false)

const formParams = reactive<SearchParams>({})
const { results, isLoading, isError, error, search } = useEquipmentSearch()

function performSearch() {
  wizardStore.selectedEquipmentId = null // Сбрасываем выбор
  search(formParams) // Запускаем поиск с текущими параметрами формы
}

function selectEquipment(id: number) {
  wizardStore.setEquipment(id)
}

function showCreateForm() {
  isCreateDialogVisible.value = true
}

function onEquipmentCreated(newItem: EquipmentOut) {
  // После успешного создания:
  isCreateDialogVisible.value = false // Закрываем диалог
  selectEquipment(newItem.id) // Сразу выбираем новый элемент
  goNext() // И сразу переходим на следующий шаг
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
