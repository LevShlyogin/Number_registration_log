<template>
  <v-container fluid class="pa-0">
    <!-- Форма поиска -->
    <div>
      <h3 class="text-h6 font-weight-medium mb-4 d-flex align-center">
        <v-icon icon="mdi-magnify" start color="grey"></v-icon>
        Поиск оборудования
      </h3>
      <v-form @submit.prevent="performSearch">
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formParams.station_object"
              label="Станция / Объект"
              variant="filled"
              flat
              hide-details="auto"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formParams.station_no"
              label="№ станционный"
              variant="filled"
              flat
              hide-details="auto"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formParams.label"
              label="Маркировка"
              variant="filled"
              flat
              hide-details="auto"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model="formParams.factory_no"
              label="№ заводской"
              variant="filled"
              flat
              hide-details="auto"
            />
          </v-col>
          <v-col cols="12">
            <v-text-field
              v-model="formParams.q"
              label="Поиск по всем полям"
              variant="filled"
              flat
              hide-details="auto"
            />
          </v-col>
        </v-row>
        <div class="mt-4">
          <v-btn type="submit" :loading="isLoading" color="primary" variant="flat" size="large">
            Поиск
          </v-btn>
          <v-btn @click="showCreateForm" variant="text" size="large" class="ml-2">
            Создать новый объект
          </v-btn>
        </div>
      </v-form>
    </div>

    <!-- Результаты поиска -->
    <div id="search-results" class="mt-8">
      <v-divider v-if="searchAttempted"></v-divider>
      <v-progress-linear
        v-if="isLoading"
        indeterminate
        color="primary"
        height="2"
      ></v-progress-linear>
      <v-alert v-if="isError" type="error" variant="tonal" class="mt-4">
        Ошибка при поиске: {{ (error as Error).message }}
      </v-alert>

      <div v-if="results" class="mt-4">
        <p v-if="results.length > 0" class="text-subtitle-1 mb-2">
          Найдено объектов: {{ results.length }}
        </p>
        <v-sheet
          v-else-if="searchAttempted"
          class="d-flex align-center justify-center text-center mx-auto pa-6"
          rounded="lg"
          color="transparent"
        >
          <div>
            <v-icon icon="mdi-database-search-outline" size="x-large" color="grey"></v-icon>
            <h2 class="text-h6 mt-4 font-weight-medium">Ничего не найдено</h2>
            <p class="text-medium-emphasis text-body-2 mt-2">
              Попробуйте изменить параметры поиска или<br />
              <v-btn
                variant="text"
                color="primary"
                @click="showCreateForm"
                size="small"
                class="mt-1"
              >
                создайте новый объект оборудования </v-btn
              >.
            </p>
          </div>
        </v-sheet>

        <v-list
          v-if="results.length > 0"
          lines="two"
          select-strategy="single-independent"
          bg-color="transparent"
        >
          <v-list-item
            v-for="item in results"
            :key="item.id"
            @click="selectEquipment(item.id)"
            :value="item.id"
            :active="wizardStore.selectedEquipmentId === item.id"
            active-color="primary"
            rounded="lg"
            class="mb-2 border pa-2"
          >
            <template #prepend>
              <v-avatar color="blue-grey-lighten-4">
                <v-icon icon="mdi-factory" color="blue-grey"></v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-bold"
              >{{ item.eq_type }} - {{ item.station_object || 'N/A' }}</v-list-item-title
            >
            <v-list-item-subtitle class="text-caption">
              Зав. №: <strong>{{ item.factory_no || '-' }}</strong> | Ст. №:
              <strong>{{ item.station_no || '-' }}</strong> | Маркировка:
              <strong>{{ item.label || '-' }}</strong>
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
        variant="flat"
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
const searchAttempted = ref(false)

const formParams = reactive<SearchParams>({})
const { results, isLoading, isError, error, search } = useEquipmentSearch()

function performSearch() {
  searchAttempted.value = true
  wizardStore.selectedEquipmentId = null
  search(formParams)
}

function selectEquipment(id: number) {
  if (wizardStore.selectedEquipmentId === id) {
    wizardStore.selectedEquipmentId = null
  } else {
    wizardStore.setEquipment(id)
  }
}

function showCreateForm() {
  isCreateDialogVisible.value = true
}

function onEquipmentCreated(newItem: EquipmentOut) {
  isCreateDialogVisible.value = false
  if (results.value) {
    results.value.unshift(newItem)
  }
  wizardStore.setEquipment(newItem.id)
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
