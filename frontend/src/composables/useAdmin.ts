import { ref, reactive, computed, watch } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type {
  SearchParams,
  AdminSearchResponse,
  AdminDocumentRow,
  DocumentUpdatePayload,
} from '@/types/api'
import apiClient from '@/api'

const fetchAdminDocuments = async (params: SearchParams): Promise<AdminSearchResponse> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )

  const { data } = await apiClient.get<AdminDocumentRow[]>('/reports/admin/documents', {
    params: filteredParams,
  })

  return { items: data, totalItems: data.length }
}

interface TableOptions {
  page: number
  itemsPerPage: number
  sortBy: { key: string; order: 'asc' | 'desc' }[]
}

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

export function useAdmin() {
  const queryClient = useQueryClient()

  const tableOptions = ref<TableOptions>({
    page: 1,
    itemsPerPage: 10,
    sortBy: [{ key: 'reg_date', order: 'desc' }],
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

  const apiQueryParams = computed(() => ({
    ...filters,
  }))

  const queryKey = ['adminDocuments', apiQueryParams]

  const { data, isLoading, isError, error } = useQuery({
    queryKey,
    queryFn: () => fetchAdminDocuments(apiQueryParams.value),
    staleTime: 1000 * 60 * 5, // 5 минут
  })

  const { mutate: saveDocument, isPending: isSaving } = useMutation({
    mutationFn: updateDocument,
    onSuccess: (updatedDocument) => {
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

  watch(
    () => filters,
    () => {
      tableOptions.value.page = 1
    },
    { deep: true },
  )

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
