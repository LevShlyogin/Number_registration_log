import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'

// API-функция для получения подсказок
const fetchDocNameSuggestions = async (query: string): Promise<string[]> => {
  if (query.length < 2) return [] // Не ищем, если меньше 2 символов

  // --- ЗАГЛУШКА API ---
  console.log('Fetching suggestions for:', query)
  await new Promise((resolve) => setTimeout(resolve, 300))

  // В будущем:
  // const { data } = await apiClient.get<string[]>('/suggest/doc-names', { params: { q: query } });
  // return data;

  // Mock-данные
  const allSuggestions = [
    'Сборочный чертеж',
    'Технические условия',
    'Габаритный чертеж',
    'Спецификация',
    'Паспорт изделия',
    'Руководство по эксплуатации',
    'Ведомость покупных изделий',
  ]
  return allSuggestions.filter((s) => s.toLowerCase().includes(query.toLowerCase()))
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

export function useDocNameSuggestions() {
  const searchQuery = ref('')

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['docNameSuggestions', searchQuery],
    queryFn: () => fetchDocNameSuggestions(searchQuery.value),
    enabled: computed(() => searchQuery.value.length >= 2), // Запрос активен, только если введено 2+ символа
  })

  return {
    searchQuery,
    suggestions,
    isLoading,
  }
}
