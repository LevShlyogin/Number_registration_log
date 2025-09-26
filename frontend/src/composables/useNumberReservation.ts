import { useMutation } from '@tanstack/vue-query'
import type { AdminReserveSpecific, ReserveNumbersIn, ReserveNumbersOut } from '@/types/api'

// Асинхронная функция для API-запроса
const reserveNumbers = async (payload: ReserveNumbersIn): Promise<ReserveNumbersOut> => {
  console.log('Reserving numbers with payload:', payload)
  await new Promise((resolve) => setTimeout(resolve, 800)) // Имитация сети

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
}

// API-функция для резерва конкретных номеров (админ)
const reserveSpecificNumbers = async (
  payload: AdminReserveSpecific,
): Promise<ReserveNumbersOut> => {
  console.log('Admin is reserving specific numbers:', payload)
  await new Promise((resolve) => setTimeout(resolve, 800))

  const mockSessionId = crypto.randomUUID()

  return {
    session_id: mockSessionId,
    reserved_numbers: payload.numbers,
  }
}

export function useNumberReservation() {
  const { mutate: reserve, isPending: isLoading } = useMutation({
    mutationFn: reserveNumbers,
  })

  const { mutate: reserveSpecific, isPending: isReservingSpecific } = useMutation({
    mutationFn: reserveSpecificNumbers,
  })

  return {
    reserve,
    isLoading,
    reserveSpecific,
    isReservingSpecific,
  }
}
