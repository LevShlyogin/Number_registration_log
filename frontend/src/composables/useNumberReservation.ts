import { useMutation } from '@tanstack/vue-query'
import type { AdminReserveSpecific, ReserveNumbersIn, ReserveNumbersOut } from '@/types/api'
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

  return {
    reserve,
    isLoading,
    reserveError,
    reserveSpecific,
    isReservingSpecific,
    reserveSpecificError,
  }
}
