import apiClient from '@/api'
import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { EquipmentOut } from '@/types/api'

export interface SearchParams {
  station_object?: string
  station_no?: string
  label?: string
  factory_no?: string
  order_no?: string
  q?: string
}

const fetchEquipment = async (params: SearchParams): Promise<EquipmentOut[]> => {
  const filteredParams = Object.fromEntries(
    Object.entries(params).filter(([, v]) => v != null && v !== ''),
  )

  const { data } = await apiClient.get<EquipmentOut[]>('/equipment/search', {
    params: filteredParams,
  })
  return data
}

export function useEquipmentSearch() {
  const searchParams = ref<SearchParams>({})

  const { data, isLoading, isError, error, refetch, isRefetching } = useQuery({
    queryKey: ['equipmentSearch', searchParams],
    queryFn: () => fetchEquipment(searchParams.value),
    enabled: false,
    retry: false,
  })

  const search = (params: SearchParams) => {
    searchParams.value = params
    return refetch()
  }

  const clearResults = () => {
    searchParams.value = {}
  }

  return {
    results: data,
    isLoading: computed(() => isLoading.value || isRefetching.value),
    isError,
    error,
    search,
    clearResults,
  }
}
