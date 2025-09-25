import { computed, reactive, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { ReportItem, ReportResponse, SearchParams } from '@/types/api'

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
      station_no: `ст.${id}`, // Добавлено
      label: `марк.${id}`, // Добавлено
      doc_name: `Чертеж ${params.q || ''} ${id}`,
      doc_no: 1000 + id,
      user: params.username || 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    }
  }).filter(Boolean) as ReportItem[]

  // Имитация фильтрации
  if (params.session_id) {
    return { totalItems: 3, items: items.slice(0, 3) }
  }
  if (params.username) {
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

  const filters = reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>({
    session_id: initialFilters.session_id,
    username: initialFilters.username,
    station_object: '',
    factory_no: '',
    date_from: '',
    date_to: '',
    doc_name: '',
    label: '',
    order_no: '',
    station_no: '',
    eq_type: '',
    q: '',
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

  // API-функция для экспорта (заглушка)
  const fetchAllReportItemsForExport = async (): Promise<ReportItem[]> => {
    const exportParams = { ...filters }
    console.log('Fetching ALL report items for export with filters:', exportParams)

    await new Promise((resolve) => setTimeout(resolve, 1500))

    return Array.from({ length: 123 }, (_, i) => ({
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
  }

  const resetFilters = () => {
    Object.assign(filters, {
      session_id: initialFilters.session_id,
      username: initialFilters.username,
      station_object: '',
      factory_no: '',
      date_from: '',
      date_to: '',
      doc_name: '',
      label: '',
      order_no: '',
      station_no: '',
      eq_type: '',
      q: '',
    })
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
