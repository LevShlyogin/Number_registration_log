import { ref, reactive, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { SearchParams, ReportResponse, ReportItem } from '@/types/api'

// API-функция для получения ОДНОЙ страницы отчета (заглушка)
const fetchReport = async (params: SearchParams): Promise<ReportResponse> => {
  console.log('Fetching report with params:', params)
  await new Promise((resolve) => setTimeout(resolve, 1000))

  const totalItems = 123
  const items: ReportItem[] = Array.from({ length: params.itemsPerPage || 10 }, (_, i) => {
    const page = params.page || 1
    const itemsPerPage = params.itemsPerPage || 10
    const id = (page - 1) * itemsPerPage + i + 1
    if (id > totalItems) return null

    return {
      id,
      eq_type: 'Турбина',
      station_object: `Мосэнерго ТЭЦ-${Math.floor(Math.random() * 20) + 1}`,
      factory_no: String(Math.floor(10000 + Math.random() * 90000)),
      station_no: `ст.${id}`,
      label: `марк.${id}`,
      doc_name: `Чертеж ${params.q || ''} ${id}`,
      doc_no: 1000 + id,
      user: params.username || 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    }
  }).filter(Boolean) as ReportItem[]

  // Имитация фильтрации
  if (params.session_id) {
    console.log(`Filtering mock data by session_id: ${params.session_id}`)
    return { totalItems: 3, items: items.slice(0, 3) }
  }
  if (params.username) {
    console.log(`Filtering mock data by username: ${params.username}`)
    return { totalItems, items }
  }

  return { totalItems, items }
}

export function useReports(initialFilters: Partial<SearchParams> = {}) {
  const tableOptions = ref({
    page: 1,
    itemsPerPage: 10,
    sortBy: [],
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

  const filters = reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>({
    ...createDefaultFilters(),
    ...initialFilters,
  })

  const queryParams = computed<SearchParams>(() => ({
    ...tableOptions.value,
    ...filters,
  }))

  const { data, isLoading, isError, error, refetch } = useQuery<ReportResponse>({
    queryKey: ['reports', queryParams],
    queryFn: () => fetchReport(queryParams.value),
  })

  const fetchAllReportItemsForExport = async (): Promise<ReportItem[]> => {
    const exportParams = { ...filters }
    console.log('Fetching ALL report items for export with filters:', exportParams)

    await new Promise((resolve) => setTimeout(resolve, 1500))
    const allItems: ReportItem[] = Array.from({ length: 123 }, (_, i) => ({
      id: i + 1,
      eq_type: 'Турбина',
      station_object: `Мосэнерго ТЭЦ-${Math.floor(Math.random() * 20) + 1}`,
      factory_no: String(Math.floor(10000 + Math.random() * 90000)),
      station_no: `ст.${i + 1}`,
      label: `марк.${i + 1}`,
      doc_name: `Чертеж ${filters.q || ''} ${i + 1}`,
      doc_no: 1000 + i + 1,
      user: 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    }))
    return allItems.filter(
      (item) =>
        (!filters.station_object || item.station_object.includes(filters.station_object)) &&
        (!filters.factory_no || item.factory_no?.includes(filters.factory_no)),
    )
  }

  const resetFilters = () => {
    const defaultFilters = createDefaultFilters()
    Object.assign(filters, defaultFilters)
    Object.assign(filters, initialFilters)
    tableOptions.value.page = 1
  }

  return {
    report: data,
    isLoading,
    isError,
    error,
    tableOptions,
    filters,
    refetch,
    resetFiltersAndRefetch: resetFilters,
    fetchAllReportItems: fetchAllReportItemsForExport,
  }
}
