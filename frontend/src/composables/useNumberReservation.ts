import { useMutation } from '@tanstack/vue-query'
import type {
  AdminReserveSpecific,
  ReserveNumbersIn,
  ReserveNumbersOut,
  AddNumbersIn,
} from '@/types/api'
import apiClient from '@/api'

// Обычный резерв
const reserveNumbers = async (payload: ReserveNumbersIn): Promise<ReserveNumbersOut> => {
  const { data } = await apiClient.post<ReserveNumbersOut>('/sessions/reserve', payload)
  return data
}

// Резерв конкретных номеров (админ)
const reserveSpecificNumbers = async (
  payload: AdminReserveSpecific,
): Promise<ReserveNumbersOut> => {
  const { data } = await apiClient.post<ReserveNumbersOut>('/admin/reserve-specific', payload)
  return data
}

// Добавление номеров в существующую сессию
const addNumbersToSession = async ({
  sessionId,
  payload,
}: {
  sessionId: string
  payload: AddNumbersIn
}): Promise<number[]> => {
  const { data } = await apiClient.post<number[]>(`/sessions/${sessionId}/add-numbers`, payload)
  return data
}

export function useNumberReservation() {
  const {
    mutate: reserve,
    isPending: isLoading,
    error: reserveError,
  } = useMutation<ReserveNumbersOut, Error, ReserveNumbersIn>({
    mutationFn: reserveNumbers,
  })

  const {
    mutate: reserveSpecific,
    isPending: isReservingSpecific,
    error: reserveSpecificError,
  } = useMutation<ReserveNumbersOut, Error, AdminReserveSpecific>({
    mutationFn: reserveSpecificNumbers,
  })

  const { mutate: addNumbers, isPending: isAdding } = useMutation<number[], Error, { sessionId: string; payload: AddNumbersIn }>({
    mutationFn: addNumbersToSession,
  })

  return {
    reserve,
    isLoading,
    reserveError,
    reserveSpecific,
    isReservingSpecific,
    reserveSpecificError,
    addNumbers,
    isAdding,
  }
}
