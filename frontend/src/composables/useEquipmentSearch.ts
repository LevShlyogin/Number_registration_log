import { ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { EquipmentOut } from '@/types/api'

export interface SearchParams {
  station_object?: string
  station_no?: string
  label?: string
  factory_no?: string
  q?: string
}

const fetchEquipment = async (params: SearchParams): Promise<EquipmentOut[]> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v != null && v !== ''),
  )

  // --- ЗАГЛУШКА API ---
  console.log('Searching equipment with params:', filteredParams)
  await new Promise((resolve) => setTimeout(resolve, 700)) // Имитация сети

  // Возвращаем mock-данные для тестирования UI
  const mockData: EquipmentOut[] = [
    {
      id: 1,
      eq_type: 'Турбина',
      station_object: 'Мосэнерго ТЭЦ-23',
      factory_no: '12345',
      order_no: 'ABC',
      label: 'ТГ-1',
      station_no: '1',
      notes: '',
    },
    {
      id: 2,
      eq_type: 'Насос',
      station_object: 'Мосэнерго ТЭЦ-23',
      factory_no: '67890',
      order_no: 'DEF',
      label: 'ПН-2',
      station_no: '2',
      notes: '',
    },
    {
      id: 3,
      eq_type: 'Турбина',
      station_object: 'Сургутская ГРЭС-2',
      factory_no: '54321',
      order_no: 'GHI',
      label: 'ТГ-8',
      station_no: '8',
      notes: '',
    },
  ]
  // Фильтруем mock-данные для имитации поиска
  if (Object.keys(filteredParams).length > 0) {
    return mockData.filter((item) =>
      Object.entries(filteredParams).every(([key, value]) =>
        String(item[key as keyof EquipmentOut])
          .toLowerCase()
          .includes(String(value).toLowerCase()),
      ),
    )
  }
  return []
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

export function useEquipmentSearch() {
  // searchParams теперь будут локальными для этого composable
  const searchParams = ref<SearchParams>({})

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['equipmentSearch', searchParams],
    queryFn: () => fetchEquipment(searchParams.value),
    enabled: false, // Запрос будет выполняться только через refetch()
    retry: false,
  })

  // Функция для запуска поиска с новыми параметрами
  const search = (params: SearchParams) => {
    searchParams.value = params
    // refetch() вернет Promise, который можно использовать для ожидания
    return refetch()
  }

  return {
    results: data,
    isLoading,
    isError,
    error,
    search,
  }
}
