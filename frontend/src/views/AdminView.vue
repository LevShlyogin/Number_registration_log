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

    <search-filters v-model="filters" @reset="resetFilters" />

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
          :disabled="!documents || documents.items.length === 0"
        >
          Экспорт в Excel
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>

      <v-data-table
        v-model:items-per-page="tableOptions.itemsPerPage"
        v-model:page="tableOptions.page"
        :headers="headers"
        :items="documents?.items || []"
        :items-length="documents?.totalItems || 0"
        :loading="isLoading"
        hover
        density="compact"
        item-value="id"
      >
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
      </v-data-table>
    </v-card>

    <edit-document-dialog
      v-model="isEditDialogOpen"
      :document="selectedDocument"
      @update="onDocumentUpdate"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as XLSX from 'xlsx'
import { useAdmin } from '@/composables/useAdmin'
import EditDocumentDialog from '@/components/admin/EditDocumentDialog.vue'
import type { AdminDocumentRow, DocumentUpdatePayload } from '@/types/api'
import SearchFilters from '@/components/common/SearchFilters.vue'
import { useNotifier } from '@/composables/useNotifier'

// --- ИЗМЕНЕНИЕ ЗДЕСЬ: Обновляем заголовки ---
const headers = [
  { title: '№ Документа', key: 'doc_no', sortable: true },
  { title: 'Дата', key: 'reg_date', sortable: true },
  { title: 'Наименование', key: 'doc_name', sortable: false },
  { title: 'Примечание', key: 'note', sortable: false }, // <-- ДОБАВЛЕНО
  { title: 'Пользователь', key: 'username', sortable: true },
  { title: '№ заказа', key: 'order_no', sortable: false }, // <-- ДОБАВЛЕНО
  { title: 'Станция/Объект', key: 'station_object', sortable: false },
  { title: 'Действия', key: 'actions', sortable: false, align: 'end' },
] as const
// --- КОНЕЦ ИЗМЕНЕНИЯ ---

const notifier = useNotifier()
const {
  documents,
  isLoading,
  tableOptions,
  filters,
  saveDocument,
  fetchAllAdminItemsForExport,
  resetFilters,
} = useAdmin()

const isEditDialogOpen = ref(false)
const selectedDocument = ref<AdminDocumentRow | null>(null)
const isExporting = ref(false)

function openEditDialog(item: AdminDocumentRow) {
  selectedDocument.value = item
  isEditDialogOpen.value = true
}

function onDocumentUpdate({ id, payload }: { id: number; payload: DocumentUpdatePayload }) {
  saveDocument(
    { id, payload },
    {
      onSuccess: () => {
        notifier.success('Запись успешно обновлена!')
        isEditDialogOpen.value = false
      },
      onError: (error) => {
        notifier.error(`Ошибка обновления: ${(error as Error).message}`)
      },
    },
  )
}

async function exportToExcel() {
  isExporting.value = true
  try {
    const allItems = await fetchAllAdminItemsForExport()
    if (!allItems || allItems.length === 0) {
      notifier.warning('Нет данных для экспорта!')
      return
    }
    const dataToExport = allItems.map((item: AdminDocumentRow) => ({
      '№ Документа': item.doc_no,
      'Дата регистрации': item.reg_date,
      'Наименование документа': item.doc_name,
      'Примечание': item.note,
      'Пользователь': item.username,
      '№ заказа': item.order_no,
      'Станция/Объект': item.station_object,
    }))
    const worksheet = XLSX.utils.json_to_sheet(dataToExport)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Админ_Отчет')
    XLSX.writeFile(workbook, `Админ_Отчет_${new Date().toISOString().split('T')[0]}.xlsx`)
  } catch (error) {
    notifier.error(`Произошла ошибка при формировании отчета: ${error}`)
  } finally {
    isExporting.value = false
  }
}
</script>
