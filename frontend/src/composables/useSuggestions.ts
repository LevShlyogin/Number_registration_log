import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import apiClient from '@/api'

const fetchDocNameSuggestions = async (query: string): Promise<string[]> => {
  if (query.length < 2) return []

  const { data } = await apiClient.get<string[]>('/suggest/doc-names', { params: { q: query } })
  return data
}

export function useDocNameSuggestions() {
  const searchQuery = ref('')

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['docNameSuggestions', searchQuery],
    queryFn: () => fetchDocNameSuggestions(searchQuery.value),
    enabled: computed(() => searchQuery.value.length >= 2),
    staleTime: 60 * 1000,
  })

  return {
    searchQuery,
    suggestions,
    isLoading,
  }
}
