import { ref, reactive } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { ReportParams, ReportResponse, ReportItem } from '@/types/api'

// API-функция для получения ОДНОЙ страницы отчета
const fetchReport = async (params: ReportParams): Promise<ReportResponse> => {
  console.log('Fetching report with params:', params)
  await new Promise((resolve) => setTimeout(resolve, 1000))

  const totalItems = 123
  const items: ReportItem[] = Array.from({ length: params.itemsPerPage }, (_, i) => {
    const id = (params.page - 1) * params.itemsPerPage + i + 1
    if (id > totalItems) return null
    return {
      id,
      eq_type: 'Турбина',
      station_object: `Мосэнерго ТЭЦ-${Math.floor(Math.random() * 20) + 1}`,
      factory_no: String(Math.floor(10000 + Math.random() * 90000)),
      doc_name: `Чертеж ${params.q || ''} ${id}`,
      doc_no: 1000 + id,
      user: 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    }
  }).filter(Boolean) as ReportItem[]

  return { totalItems, items }
}

export function useReports() {
  const tableOptions = ref({
    page: 1,
    itemsPerPage: 10,
    sortBy: [],
  })
  const filters = reactive({
    station_object: '',
    factory_no: '',
    date_from: '',
    date_to: '',
    q: '',
  })

  const { data, isLoading, isError, error, refetch } = useQuery<ReportResponse>({
    queryKey: ['reports', tableOptions, filters],
    queryFn: () => fetchReport({ ...tableOptions.value, ...filters }),
  })

  // --- НОВАЯ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ВСЕХ ДАННЫХ ДЛЯ ЭКСПОРТА ---
  const fetchAllReportItems = async (): Promise<ReportItem[]> => {
    console.log('Fetching ALL report items for export with filters:', filters)

    // В реальном API здесь будет запрос к отдельному эндпоинту
    // GET /reports/export?station_object=...&factory_no=...
    // const { data } = await apiClient.get<ReportItem[]>('/reports/export', { params: filters });
    // return data;

    // --- ЗАГЛУШКА ДЛЯ ЭКСПОРТА ---
    // Генерируем все 123 элемента для имитации полной выгрузки
    await new Promise((resolve) => setTimeout(resolve, 1500)) // Имитируем более долгую загрузку
    const allItems: ReportItem[] = Array.from({ length: 123 }, (_, i) => ({
      id: i + 1,
      eq_type: 'Турбина',
      station_object: `Мосэнерго ТЭЦ-${Math.floor(Math.random() * 20) + 1}`,
      factory_no: String(Math.floor(10000 + Math.random() * 90000)),
      doc_name: `Чертеж ${filters.q || ''} ${i + 1}`,
      doc_no: 1000 + i + 1,
      user: 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    }))
    // Фильтруем mock-данные, если нужно
    return allItems.filter(
      (item) =>
        (!filters.station_object || item.station_object.includes(filters.station_object)) &&
        (!filters.factory_no || item.factory_no?.includes(filters.factory_no)),
    )
    // --- КОНЕЦ ЗАГЛУШКИ ---
  }

  // Функция для сброса фильтров и перезагрузки
  const resetFiltersAndRefetch = () => {
    Object.assign(filters, {
      station_object: '',
      factory_no: '',
      date_from: '',
      date_to: '',
      q: '',
    })
  }

  return {
    report: data,
    isLoading,
    isError,
    error,
    tableOptions,
    filters,
    refetch,
    resetFiltersAndRefetch,
    fetchAllReportItems,
  }
}
