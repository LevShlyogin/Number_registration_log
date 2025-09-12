<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1 class="text-h4 font-weight-bold mb-4">Отчеты</h1>
        <p class="text-body-1 text-grey mb-6">
          Просмотр и фильтрация всех зарегистрированных номеров.
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
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="filters.station_object"
              label="Станция / Объект"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="filters.factory_no"
              label="Заводской номер"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-text-field
              v-model="filters.q"
              label="Поиск по всем полям"
              clearable
              hide-details="auto"
            ></v-text-field>
          </v-col>
          <!-- TODO: Добавить поля для дат (v-date-picker) -->
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
        :search="filters.q"
        item-value="id"
        class="elevation-0"
        hover
        @update:options="loadItems"
      >
        <!-- Можно добавить кастомные слоты для форматирования ячеек -->
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

const headers = [
  { title: 'Станция/Объект', key: 'station_object', sortable: true },
  { title: 'Зав. №', key: 'factory_no', sortable: true },
  { title: 'Документ', key: 'doc_name', sortable: false },
  { title: 'Номер', key: 'doc_no', sortable: true },
  { title: 'Пользователь', key: 'user', sortable: true },
  { title: 'Дата', key: 'created', sortable: true },
]

const { report, isLoading, tableOptions, filters, refetch, resetFiltersAndRefetch } = useReports()

// Эта функция будет вызываться v-data-table-server при изменении пагинации или сортировки
function loadItems() {
  // refetch() не всегда нужен, т.к. useQuery реактивен к tableOptions.
  // Но для явного контроля можно его использовать.
  // refetch();
}

// TODO: Реализовать функцию экспорта
function exportToExcel() {
  alert('Функционал экспорта в разработке...')
}
</script>
