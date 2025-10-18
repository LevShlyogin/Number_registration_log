import { ref, reactive, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type {
  SearchParams,
  AdminSearchResponse,
  AdminDocumentRow,
  DocumentUpdatePayload,
} from '@/types/api'
import apiClient from '@/api'

// --- РЕАЛЬНЫЕ API ФУНКЦИИ ---

/**
 * Получает данные для админской таблицы с сервера.
 * @param params - Параметры фильтрации и пагинации.
 */
const fetchAdminDocuments = async (params: SearchParams): Promise<AdminSearchResponse> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )

  const { data } = await apiClient.get<AdminDocumentRow[]>('/reports/admin/documents', {
    params: filteredParams,
  })

  // Как и в отчетах, оборачиваем в объект для пагинации
  return { items: data, totalItems: data.length }
}

/**
 * Обновляет данные документа на сервере.
 * @param id - ID документа.
 * @param payload - Данные для обновления.
 */
const updateDocument = async ({
  id,
  payload,
}: {
  id: number
  payload: DocumentUpdatePayload
}): Promise<AdminDocumentRow> => {
  const { data } = await apiClient.patch<AdminDocumentRow>(`/documents/${id}`, payload)
  return data
}

/**
 * Получает ВСЕ данные для экспорта из админки.
 * @param params - Только параметры фильтрации.
 */
const fetchAllAdminItemsForExport = async (
  params: Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>,
): Promise<AdminDocumentRow[]> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )
  const { data } = await apiClient.get<AdminDocumentRow[]>('/reports/admin/documents', {
    params: filteredParams,
  })
  return data
}

// --- КОМПОЗАБЛ ---

export function useAdmin() {
  const queryClient = useQueryClient()

  const tableOptions = ref({
    page: 1,
    itemsPerPage: 10,
    sortBy: [],
  })

  const createDefaultFilters = () => ({
    station_object: '',
    factory_no: '',
    station_no: '',
    label: '',
    order_no: '',
    username: '',
    doc_name: '',
    date_from: '',
    date_to: '',
    eq_type: '',
    q: '',
    session_id: undefined,
  })

  const filters =
    reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>(createDefaultFilters())

  const queryParams = computed(() => ({
    ...tableOptions.value,
    ...filters,
  }))

  const queryKey = ['adminDocuments', queryParams]

  // Query для получения данных
  const { data, isLoading, isError, error } = useQuery({
    queryKey,
    queryFn: () => fetchAdminDocuments(queryParams.value),
  })

  // Mutation для сохранения изменений
  const { mutate: saveDocument, isPending: isSaving } = useMutation({
    mutationFn: updateDocument,
    onSuccess: (updatedDocument) => {
      // При успехе обновляем кэш, чтобы UI мгновенно отразил изменения
      queryClient.setQueryData<AdminSearchResponse>(queryKey, (oldData) => {
        if (!oldData) return oldData
        return {
          ...oldData,
          items: oldData.items.map((item) =>
            item.id === updatedDocument.id ? { ...item, ...updatedDocument } : item,
          ),
        }
      })
    },
  })

  const resetFilters = () => {
    Object.assign(filters, createDefaultFilters())
    tableOptions.value.page = 1
  }

  return {
    documents: data,
    isLoading,
    isError,
    error,
    tableOptions,
    filters,
    saveDocument,
    isSaving,
    fetchAllAdminItemsForExport: () => fetchAllAdminItemsForExport(filters),
    resetFilters,
  }
}
