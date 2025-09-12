import { ref, reactive, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { ReportParams, ReportResponse, ReportItem } from '@/types/api'

// API-функция
const fetchReport = async (params: ReportParams): Promise<ReportResponse> => {
  // --- ЗАГЛУШКА API ---
  console.log('Fetching report with params:', params)
  await new Promise(resolve => setTimeout(resolve, 1000));

  // В будущем:
  // const { data } = await apiClient.get<ReportResponse>('/reports', { params });
  // return data;

  // Генерируем mock-данные
  const totalItems = 123;
  const items: ReportItem[] = Array.from({ length: params.itemsPerPage }, (_, i) => {
    const id = (params.page - 1) * params.itemsPerPage + i + 1;
    if (id > totalItems) return null;
    return {
      id,
      eq_type: 'Турбина',
      station_object: `Мосэнерго ТЭЦ-${Math.floor(Math.random() * 20) + 1}`,
      factory_no: String(Math.floor(10000 + Math.random() * 90000)),
      doc_name: `Чертеж ${params.q || ''} ${id}`,
      doc_no: 1000 + id,
      user: 'yuaalekseeva',
      created: new Date(Date.now() - i * 1000 * 3600 * 24).toISOString(),
    };
  }).filter(Boolean) as ReportItem[];

  return { totalItems, items };
  // --- КОНЕЦ ЗАГЛУШКИН ---
}

export function useReports() {
  // Состояние для таблицы: пагинация, сортировка
  const tableOptions = ref({
    page: 1,
    itemsPerPage: 10,
    sortBy: [],
  });

  // Состояние для фильтров
  const filters = reactive({
    station_object: '',
    factory_no: '',
    date_from: '',
    date_to: '',
    q: '',
  });

  // Query, который зависит и от опций таблицы, и от фильтров
  const { data, isLoading, isError, error, refetch } = useQuery<ReportResponse>({
    queryKey: ['reports', tableOptions, filters],
    queryFn: () => fetchReport({ ...tableOptions.value, ...filters }),
  })

  // Функция для сброса фильтров и перезагрузки
  const resetFiltersAndRefetch = () => {
    Object.assign(filters, {
      station_object: '',
      factory_no: '',
      date_from: '',
      date_to: '',
      q: '',
    });
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
  }
}