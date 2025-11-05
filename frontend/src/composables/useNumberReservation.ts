import { useMutation } from '@tanstack/vue-query'
import type {
  ReserveNumbersIn,
  ReserveNumbersOut,
  AddNumbersIn,
  GoldenNumberReservationIn,
} from '@/types/api'
import apiClient from '@/api'

const reserveNumbers = async (payload: ReserveNumbersIn): Promise<ReserveNumbersOut> => {
  const { data } = await apiClient.post<ReserveNumbersOut>('/sessions/reserve', payload)
  return data
}

const reserveGoldenNumbers = async (
  payload: GoldenNumberReservationIn,
): Promise<ReserveNumbersOut> => {
  const { data } = await apiClient.post<ReserveNumbersOut>('/documents/reserve-golden', payload)
  return data
}

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
  } = useMutation<ReserveNumbersOut, Error, ReserveNumbersIn>({ mutationFn: reserveNumbers })

  const {
    mutate: reserveGolden,
    isPending: isReservingGolden,
    error: reserveGoldenError,
  } = useMutation<ReserveNumbersOut, Error, GoldenNumberReservationIn>({
    mutationFn: reserveGoldenNumbers,
  })

  const {
    mutate: addNumbers,
    isPending: isAdding,
    error: addNumbersError,
  } = useMutation<number[], Error, { sessionId: string; payload: AddNumbersIn }>({
    mutationFn: addNumbersToSession,
  })

  return {
    reserve,
    isLoading,
    reserveError,
    reserveGolden,
    isReservingGolden,
    reserveGoldenError,
    addNumbers,
    isAdding,
    addNumbersError,
  }
}
