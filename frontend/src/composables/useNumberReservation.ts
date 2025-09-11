import { useMutation } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { ReserveNumbersIn, ReserveNumbersOut } from '@/types/api'

// Асинхронная функция для API-запроса
const reserveNumbers = async (payload: ReserveNumbersIn): Promise<ReserveNumbersOut> => {
  // --- ЗАГЛУШКА API ---
  console.log('Reserving numbers with payload:', payload)
  await new Promise((resolve) => setTimeout(resolve, 800)) // Имитация сети

  // В будущем здесь будет реальный запрос:
  // const { data } = await apiClient.post<ReserveNumbersOut>('/sessions/reserve', payload);
  // return data;

  // Возвращаем mock-данные
  if (payload.quantity <= 0) {
    throw new Error('Количество должно быть больше нуля')
  }
  const mockSessionId = crypto.randomUUID() // Генерируем случайный UUID
  const mockReservedNumbers = Array.from({ length: payload.quantity }, (_, i) => 1000 + i)
  const mockResponse: ReserveNumbersOut = {
    session_id: mockSessionId,
    reserved_numbers: mockReservedNumbers,
  }
  console.log('Mock response for reservation:', mockResponse)
  return mockResponse
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

export function useNumberReservation() {
  const { mutate, isPending, isError, error, data } = useMutation({
    mutationFn: reserveNumbers,
  })

  return {
    reserve: mutate,
    isLoading: isPending,
    isError,
    error,
    result: data,
  }
}
