import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { AssignNumberIn, AssignNumberOut, AssignedNumber } from '@/types/api'

// --- API-функции ---

// Получение уже назначенных номеров для текущей сессии
const fetchAssignedNumbers = async (sessionId: string): Promise<AssignedNumber[]> => {
  // --- ЗАГЛУШКА API ---
  console.log('Fetching assigned numbers for session:', sessionId)
  await new Promise((resolve) => setTimeout(resolve, 400))
  // В будущем:
  // const { data } = await apiClient.get<AssignedNumber[]>(`/sessions/${sessionId}/assigned`);
  // return data;

  // Возвращаем пустой массив, т.к. в начале назначенных номеров нет
  // (но можно добавить mock-данные для теста)
  return []
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

// Назначение следующего свободного номера
const assignNextNumber = async (payload: AssignNumberIn): Promise<AssignNumberOut> => {
  // --- ЗАГЛУШКА API ---
  console.log('Assigning next number with payload:', payload)
  await new Promise((resolve) => setTimeout(resolve, 600))
  // В будущем:
  // const { data } = await apiClient.post<AssignNumberOut>('/sessions/assign', payload);
  // return data;

  // Возвращаем mock-ответ
  const mockResponse: AssignNumberOut = {
    session_id: payload.session_id,
    doc_no: Math.floor(1000 + Math.random() * 900), // Случайный номер
    doc_name: payload.doc_name,
    created: new Date().toISOString(),
    user: 'yuaalekseeva', // Заглушка
  }
  console.log('Mock response for assignment:', mockResponse)
  return mockResponse
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

export function useNumberAssignment(sessionId: string) {
  const queryClient = useQueryClient()
  const queryKey = ['assignedNumbers', sessionId] // Уникальный ключ для запроса

  // Query для получения списка назначенных номеров
  const {
    data: assignedNumbers,
    isLoading: isLoadingAssigned,
    isError: isErrorAssigned,
  } = useQuery({
    queryKey,
    queryFn: () => fetchAssignedNumbers(sessionId),
    enabled: !!sessionId, // Выполнять только если есть sessionId
  })

  // Mutation для назначения нового номера
  const {
    mutate: assignNumber,
    isPending: isAssigning,
    isError: isErrorAssigning,
    error: errorAssigning,
  } = useMutation({
    mutationFn: assignNextNumber,
    // При успехе мутации мы хотим обновить список назначенных номеров
    onSuccess: (newlyAssignedNumber) => {
      // Обновляем кеш useQuery, добавляя новый элемент
      // Это вызовет автоматическое обновление UI без нового API-запроса
      queryClient.setQueryData<AssignedNumber[]>(queryKey, (oldData) => {
        const newEntry: AssignedNumber = {
          doc_no: newlyAssignedNumber.doc_no,
          doc_name: newlyAssignedNumber.doc_name,
        }
        return oldData ? [...oldData, newEntry] : [newEntry]
      })
    },
  })

  return {
    assignedNumbers,
    isLoadingAssigned,
    isErrorAssigned,
    assignNumber,
    isAssigning,
    isErrorAssigning,
    errorAssigning,
  }
}
