<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1 class="text-h4 font-weight-bold mb-4">Отчеты</h1>
        <p class="text-body-1 text-grey mb-6">
          Просмотр, фильтрация и экспорт всех зарегистрированных номеров.
        </p>
      </v-col>
    </v-row>

    <!-- Используем унифицированный компонент фильтров -->
    <search-filters v-model="filters" @reset="resetFilters" />

    <!-- Таблица с результатами -->
    <v-card flat class="border">
      <v-card-title class="d-flex align-center">
        Результаты
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-file-excel-outline"
          @click="exportToExcel"
          :loading="isExporting"
          :disabled="!report || report.items.length === 0"
        >
          Экспорт в Excel
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <!-- v-data-table-server для работы с серверными данными -->
      <v-data-table-server
        v-model:items-per-page="tableOptions.itemsPerPage"
        v-model:page="tableOptions.page"
        v-model:sort-by="tableOptions.sortBy"
        :headers="headers"
        :items="report?.items || []"
        :items-length="report?.totalItems || 0"
        :loading="isLoading"
        item-value="id"
        class="elevation-0"
        hover
        density="compact"
      >
        <template #[`item.created`]="{ value }">
          {{ value ? new Date(value).toLocaleDateString() : '-' }}
        </template>

        <template #no-data>
          <div class="text-center pa-6">
            <v-icon
              icon="mdi-database-off-outline"
              size="x-large"
              color="grey-lighten-1"
              class="mb-4"
            ></v-icon>
            <h3 class="text-h6 font-weight-medium">Нет данных для отображения</h3>
            <p class="text-medium-emphasis text-body-2 mt-2">
              Попробуйте изменить или сбросить фильтры.
            </p>
          </div>
        </template>

        <template #loading>
          <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
        </template>
      </v-data-table-server>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useReports } from '@/composables/useReports'
import { useAuthStore } from '@/stores/auth'
import * as XLSX from 'xlsx'
import type { ReportItem, SearchParams } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'
import SearchFilters from '@/components/common/SearchFilters.vue'

const authStore = useAuthStore()
const notifier = useNotifier()

const lastSessionId = history.state.lastSessionId as string | undefined
let initialFilters: Partial<SearchParams> = {}
if (lastSessionId) {
  // Если пришли из шага, фильтруем по ID сессии
  initialFilters = { session_id: lastSessionId }
} else if (authStore.user) {
  // Иначе фильтруем по имени текущего пользователя
  initialFilters = { username: authStore.user.login }
}

const { report, isLoading, tableOptions, filters, resetFiltersAndRefetch, fetchAllReportItems } =
  useReports(initialFilters)

const isExporting = ref(false)

const headers = [
  { title: '№ Документа', key: 'doc_no', sortable: true },
  { title: 'Дата регистрации', key: 'created', sortable: true },
  { title: 'Наименование документа', key: 'doc_name', sortable: false },
  { title: 'Пользователь', key: 'user', sortable: true },
  { title: 'Станция/Объект', key: 'station_object', sortable: false },
  { title: 'Тип оборуд.', key: 'eq_type', sortable: false },
  { title: 'Зав. №', key: 'factory_no', sortable: false },
  { title: 'Ст. №', key: 'station_no', sortable: false },
  { title: 'Маркировка', key: 'label', sortable: false },
] as const

onMounted(() => {
  if (history.state.lastSessionId) {
    history.replaceState({ ...history.state, lastSessionId: undefined }, '')
  }
})

function resetFilters() {
  resetFiltersAndRefetch()
}

async function exportToExcel() {
  isExporting.value = true
  try {
    const allItems = await fetchAllReportItems()

    if (!allItems || allItems.length === 0) {
      notifier.warning('Нет данных для экспорта!')
      return
    }

    const dataToExport = allItems.map((item: ReportItem) => ({
      '№ Документа': item.doc_no,
      'Дата регистрации': new Date(item.created).toLocaleDateString(),
      'Наименование документа': item.doc_name,
      'Пользователь': item.user,
      'Станция/Объект': item.station_object,
      'Тип оборуд.': item.eq_type,
      'Зав. №': item.factory_no,
      'Ст. №': item.station_no,
      'Маркировка': item.label,
    }))

    const worksheet = XLSX.utils.json_to_sheet(dataToExport)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Отчет')
    XLSX.writeFile(workbook, `Отчет_Регистрации_${new Date().toISOString().split('T')[0]}.xlsx`)
  } catch (error) {
    console.error('Ошибка при экспорте в Excel:', error)
    notifier.error('Произошла ошибка при формировании отчета для экспорта.')
  } finally {
    isExporting.value = false
  }
}
</script>
