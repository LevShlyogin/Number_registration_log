import { ref, reactive, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type {
  SearchParams,
  AdminSearchResponse,
  AdminDocumentRow,
  DocumentUpdatePayload,
} from '@/types/api'

const mockAdminData: AdminDocumentRow[] = Array.from({ length: 57 }, (_, i) => ({
  id: i + 1,
  doc_no: 1001 + i,
  reg_date: new Date(Date.now() - i * 1000 * 3600 * 12).toISOString(),
  doc_name: `Техническое задание ${i + 1}`,
  note: i % 3 === 0 ? `Важное примечание ${i + 1}` : null,
  eq_id: 200 + i,
  eq_type: i % 2 === 0 ? 'Турбина' : 'Насос',
  factory_no: `FN-${Math.floor(10000 + Math.random() * 90000)}`,
  order_no: `ON-${Math.floor(100 + Math.random() * 900)}`,
  label: `ТГ-${i + 1}`,
  station_no: `${i + 1}`,
  station_object: `Мосэнерго ТЭЦ-${Math.floor(1 + Math.random() * 25)}`,
  username: i % 2 === 0 ? 'yuaalekseeva' : 'sidorov',
}))

const fetchAdminDocuments = async (params: SearchParams): Promise<AdminSearchResponse> => {
  console.log('Fetching admin documents with params:', params)
  await new Promise((resolve) => setTimeout(resolve, 1000))
  return { items: mockAdminData.slice(0, params.itemsPerPage), totalItems: mockAdminData.length }
}

const updateDocument = async ({
  id,
  payload,
}: {
  id: number
  payload: DocumentUpdatePayload
}): Promise<AdminDocumentRow> => {
  console.log(`Updating document ${id} with payload:`, payload)
  await new Promise((resolve) => setTimeout(resolve, 600))
  const existing = mockAdminData.find((d) => d.id === id)
  if (!existing) throw new Error('Document not found')
  const updated = { ...existing, ...payload }
  const index = mockAdminData.findIndex((d) => d.id === id)
  if (index !== -1) mockAdminData[index] = updated
  return updated
}

export function useAdmin() {
  const queryClient = useQueryClient()
  const queryKey = ['adminDocuments']

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
  })

  const filters =
    reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>(createDefaultFilters())

  const queryParams = computed(() => ({
    ...tableOptions.value,
    ...filters,
  }))

  const { data, isLoading, isError, error } = useQuery({
    queryKey: [...queryKey, queryParams],
    queryFn: () => fetchAdminDocuments(queryParams.value),
  })

  const { mutate: saveDocument, isPending: isSaving } = useMutation({
    mutationFn: updateDocument,
    onSuccess: (updatedDocument) => {
      queryClient.setQueryData<AdminSearchResponse>([...queryKey, queryParams], (oldData) => {
        if (!oldData) return oldData
        return {
          ...oldData,
          items: oldData.items.map((item) =>
            item.id === updatedDocument.id ? updatedDocument : item,
          ),
        }
      })
    },
  })

  const fetchAllAdminItemsForExport = async (): Promise<AdminDocumentRow[]> => {
    const exportParams = { ...filters }
    console.log('Fetching ALL admin documents for export with filters:', exportParams)
    await new Promise((resolve) => setTimeout(resolve, 1500))
    return mockAdminData
  }

  // Улучшенная функция сброса
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
    fetchAllAdminItemsForExport,
    resetFilters,
  }
}
