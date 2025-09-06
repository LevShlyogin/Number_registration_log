import { ref, watch, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { EquipmentOut } from '@/types/api'

// Типы для параметров поиска
export interface SearchParams {
  station_object?: string
  station_no?: string
  label?: string
  factory_no?: string
  order_no?: string
  q?: string
}

// Асинхронная функция для API-запроса
const fetchEquipment = async (params: SearchParams) => {
  // Фильтруем пустые параметры, чтобы не отправлять их
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([_, v]) => v != null && v !== ''),
  )

  const { data } = await apiClient.get<EquipmentOut[]>('/equipment/search', {
    params: filteredParams,
  })
  return data
}

export function useEquipmentSearch(searchParams: Ref<SearchParams>) {
  // ref для триггера запроса "по требованию"
  const isSearchTriggered = ref(false)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['equipmentSearch', searchParams], // Ключ зависит от параметров поиска
    queryFn: () => fetchEquipment(searchParams.value),
    enabled: isSearchTriggered, // Запрос выполняется только когда isSearchTriggered = true
    retry: false,
  })

  // Функция для запуска поиска
  const search = () => {
    isSearchTriggered.value = true
    // refetch() не всегда нужен, т.к. изменение isSearchTriggered на true само запустит запрос
    // Но если нужно перезапросить с теми же параметрами, refetch() полезен.
  }

  // Сбрасываем триггер, если параметры поиска очищаются
  watch(
    searchParams,
    (newParams) => {
      const allEmpty = Object.values(newParams).every((v) => !v)
      if (allEmpty) {
        isSearchTriggered.value = false
      }
    },
    { deep: true },
  )

  return {
    results: data,
    isLoading,
    isError,
    error,
    search,
  }
}
