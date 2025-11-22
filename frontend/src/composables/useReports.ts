import { ref, reactive, computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { SearchParams, ReportResponse, ReportItem } from '@/types/api'
import apiClient from '@/api'

const fetchReport = async (params: SearchParams): Promise<ReportResponse> => {
  // Убираем пустые значения
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )

  const { data } = await apiClient.get<ReportItem[]>('/reports', { params: filteredParams })

  return { items: data, totalItems: data.length }
}

interface TableOptions {
  page: number
  itemsPerPage: number
  sortBy: { key: string; order: 'asc' | 'desc' }[]
}

const fetchAllReportItemsForExport = async (
  params: Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>,
): Promise<ReportItem[]> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )
  const { data } = await apiClient.get<ReportItem[]>('/reports', { params: filteredParams })
  return data
}

export function useReports(initialFilters: Partial<SearchParams> = {}) {
  // Состояние для настроек таблицы (только UI)
  const tableOptions = ref<TableOptions>({
    page: 1,
    itemsPerPage: 10,
    sortBy: [{ key: 'reg_date', order: 'desc' }],
  })

  const createDefaultFilters = () => ({
    session_id: undefined,
    username: undefined,
    station_object: '',
    factory_no: '',
    station_no: '',
    label: '',
    order_no: '',
    doc_name: '',
    date_from: '',
    date_to: '',
    eq_type: '',
    q: '',
  })

  // Реактивный объект фильтров
  const filters = reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>({
    ...createDefaultFilters(),
    ...initialFilters,
  })

  // Пагинация и сортировка происходят на клиенте.
  const apiQueryParams = computed<SearchParams>(() => ({
    ...filters,
  }))

  // TanStack Query
  const { data, isLoading, isError, error } = useQuery<ReportResponse>({
    queryKey: ['reports', apiQueryParams],
    queryFn: () => fetchReport(apiQueryParams.value),
    staleTime: 1000 * 60 * 5, // Кэшируем на 5 минут
  })

  // Если фильтры изменились -> на первую страницу
  watch(
    () => filters,
    () => {
      tableOptions.value.page = 1
    },
    { deep: true },
  )

  // Функция сброса
  const resetFilters = () => {
    Object.assign(filters, createDefaultFilters(), initialFilters)
    tableOptions.value.page = 1
  }

  return {
    report: data,
    isLoading,
    isError,
    error,
    tableOptions,
    filters,
    resetFiltersAndRefetch: resetFilters,
    fetchAllReportItemsForExport: () => fetchAllReportItemsForExport(filters),
  }
}
