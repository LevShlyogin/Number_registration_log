import { ref, reactive, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { SearchParams, ReportResponse, ReportItem } from '@/types/api'
import apiClient from '@/api'

// --- РЕАЛЬНЫЕ API ФУНКЦИИ ---

/**
 * Получает данные для отчета с сервера.
 * @param params - Параметры фильтрации и пагинации.
 */
const fetchReport = async (params: SearchParams): Promise<ReportResponse> => {
  // Убираем пустые/null значения, чтобы не передавать их в URL
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )

  // Делаем реальный запрос к бэкенду
  const { data } = await apiClient.get<ReportItem[]>('/reports', { params: filteredParams })

  // Бэкенд возвращает простой массив. Для пагинации v-data-table-server
  // нам нужна структура { items, totalItems }.
  // Так как бэкенд не возвращает общее количество, мы будем использовать
  // длину полученного массива. Это означает, что пагинация будет работать
  // только на клиенте для уже загруженных данных.
  // Для настоящей серверной пагинации бэкенд должен возвращать `totalItems`.
  return { items: data, totalItems: data.length }
}

/**
 * Получает ВСЕ данные для экспорта, игнорируя пагинацию.
 * @param params - Только параметры фильтрации.
 */
const fetchAllReportItemsForExport = async (
  params: Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>,
): Promise<ReportItem[]> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )
  const { data } = await apiClient.get<ReportItem[]>('/reports', { params: filteredParams })
  return data
}

// --- КОМПОЗАБЛ ---

export function useReports(initialFilters: Partial<SearchParams> = {}) {
  // Состояние для настроек таблицы (пагинация, сортировка)
  const tableOptions = ref({
    page: 1,
    itemsPerPage: 10,
    sortBy: [],
  })

  // Функция для создания объекта фильтров по умолчанию
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

  // Реактивный объект с текущими значениями фильтров
  const filters = reactive<Omit<SearchParams, 'page' | 'itemsPerPage' | 'sortBy'>>({
    ...createDefaultFilters(),
    ...initialFilters,
  })

  // Вычисляемое свойство, которое объединяет фильтры и опции таблицы
  // в один объект для отправки на сервер.
  const queryParams = computed<SearchParams>(() => ({
    ...tableOptions.value,
    ...filters,
  }))

  // TanStack Query для получения и кэширования данных отчета
  const { data, isLoading, isError, error } = useQuery<ReportResponse>({
    queryKey: ['reports', queryParams], // Ключ кэша зависит от параметров
    queryFn: () => fetchReport(queryParams.value),
  })

  // Функция сброса фильтров к начальному состоянию
  const resetFilters = () => {
    Object.assign(filters, createDefaultFilters(), initialFilters)
    tableOptions.value.page = 1 // Сбрасываем на первую страницу
  }

  return {
    report: data,
    isLoading,
    isError,
    error,
    tableOptions,
    filters,
    resetFiltersAndRefetch: resetFilters, // Переименовано для ясности
    fetchAllReportItemsForExport: () => fetchAllReportItemsForExport(filters), // Передаем текущие фильтры
  }
}
