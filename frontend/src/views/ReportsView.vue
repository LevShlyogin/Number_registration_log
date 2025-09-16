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

    <!-- Карточка с фильтрами -->
    <v-card flat class="border mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon start icon="mdi-filter-variant"></v-icon>
        Фильтры
        <v-spacer></v-spacer>
        <v-btn size="small" variant="text" prepend-icon="mdi-close" @click="resetFiltersAndRefetch">
          Сбросить
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.station_object"
              label="Станция / Объект"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.factory_no"
              label="Заводской номер"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="filters.q"
              label="Поиск по всем полям"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3" class="d-flex align-center">
            <v-text-field
              v-model="filters.date_from"
              label="Дата с"
              type="date"
              clearable
              hide-details="auto"
              class="mr-2"
            ></v-text-field>
            <v-text-field
              v-model="filters.date_to"
              label="Дата по"
              type="date"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

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
        @update:options="loadItems"
      >
        <template #[`item.created`]="{ item }">
          {{ new Date(item.created).toLocaleDateString() }}
        </template>
      </v-data-table-server>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useReports } from '@/composables/useReports'
import * as XLSX from 'xlsx'
import type { ReportItem } from '@/types/api'

const headers = [
  { title: 'Станция/Объект', key: 'station_object', sortable: true },
  { title: 'Зав. №', key: 'factory_no', sortable: true },
  { title: 'Документ', key: 'doc_name', sortable: false },
  { title: 'Номер', key: 'doc_no', sortable: true },
  { title: 'Пользователь', key: 'user', sortable: true },
  { title: 'Дата', key: 'created', sortable: true },
]

const { report, isLoading, tableOptions, filters, resetFiltersAndRefetch, fetchAllReportItems } =
  useReports()

const isExporting = ref(false)

function loadItems() {}

async function exportToExcel() {
  isExporting.value = true
  try {
    const allItems = await fetchAllReportItems()

    if (!allItems || allItems.length === 0) {
      alert('Нет данных для экспорта!')
      return
    }

    const dataToExport = allItems.map((item: ReportItem) => ({
      'Станция/Объект': item.station_object,
      'Зав. №': item.factory_no,
      Документ: item.doc_name,
      Номер: item.doc_no,
      Пользователь: item.user,
      Дата: new Date(item.created).toLocaleDateString(),
    }))

    const worksheet = XLSX.utils.json_to_sheet(dataToExport)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Отчет')
    XLSX.writeFile(workbook, `Отчет_Регистрации_${new Date().toISOString().split('T')[0]}.xlsx`)
  } catch (error) {
    console.error('Ошибка при экспорте в Excel:', error)
    alert('Произошла ошибка при формировании отчета для экспорта.')
  } finally {
    isExporting.value = false
  }
}
</script>
