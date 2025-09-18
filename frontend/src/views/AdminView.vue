<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <h1 class="text-h4 font-weight-bold mb-4">
          <v-icon icon="mdi-shield-crown-outline" start></v-icon>
          Панель Администратора
        </h1>
      </v-col>
    </v-row>

    <v-card flat class="border mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon start icon="mdi-filter-variant"></v-icon>
        Фильтры поиска
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.station_object"
              label="Станция/Объект"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.station_no"
              label="№ станционный"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.label"
              label="Маркировка"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.factory_no"
              label="№ заводской"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.order_no"
              label="№ заказа"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.username"
              label="Пользователь"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.date_from"
              label="Дата от"
              type="date"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
          <v-col cols="12" sm="6" md="3"
            ><v-text-field
              v-model="filters.date_to"
              label="Дата до"
              type="date"
              clearable
              hide-details="auto"
            ></v-text-field
          ></v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card flat class="border">
      <v-card-title class="d-flex align-center">
        Результаты
        <v-spacer></v-spacer>
        <!-- TODO: Добавить экспорт -->
      </v-card-title>
      <v-data-table-server
        v-model:items-per-page="tableOptions.itemsPerPage"
        v-model:page="tableOptions.page"
        v-model:sort-by="tableOptions.sortBy"
        :headers="headers"
        :items="documents?.items || []"
        :items-length="documents?.totalItems || 0"
        :loading="isLoading"
        hover
        density="compact"
      >
        <template #[`item.reg_date`]="{ value }">
          {{ value ? new Date(value).toLocaleDateString() : '-' }}
        </template>
        <template #[`item.actions`]="{ item }">
          <v-btn
            icon="mdi-pencil"
            variant="text"
            size="small"
            @click="openEditDialog(item)"
          ></v-btn>
        </template>
        <template #loading><v-skeleton-loader type="table-row@10"></v-skeleton-loader></template>
        <template #no-data><div class="text-center pa-4">Нет данных</div></template>
      </v-data-table-server>
    </v-card>

    <edit-document-dialog
      v-model="isEditDialogOpen"
      :document="selectedDocument"
      @success="onDocumentUpdate"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAdmin } from '@/composables/useAdmin'
import EditDocumentDialog from '@/components/admin/EditDocumentDialog.vue'
import type { AdminDocumentRow, DocumentUpdatePayload } from '@/types/api'

const headers = [
  { title: '№ док.', key: 'doc_no' },
  { title: 'Дата', key: 'reg_date' },
  { title: 'Наименование', key: 'doc_name' },
  { title: 'Станция/Объект', key: 'station_object', sortable: false },
  { title: 'Зав. №', key: 'factory_no', sortable: false },
  { title: 'Пользователь', key: 'username' },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
] as const

const { documents, isLoading, tableOptions, filters, saveDocument } = useAdmin()

const isEditDialogOpen = ref(false)
const selectedDocument = ref<AdminDocumentRow | null>(null)

function openEditDialog(item: AdminDocumentRow) {
  selectedDocument.value = item
  isEditDialogOpen.value = true
}

function onDocumentUpdate({ id, payload }: { id: number; payload: DocumentUpdatePayload }) {
  saveDocument(
    { id, payload },
    {
      onSuccess: () => {
        // Уведомление об успехе можно добавить здесь
        isEditDialogOpen.value = false
      },
      onError: () => {
        // Уведомление об ошибке
      },
    },
  )
}
</script>
