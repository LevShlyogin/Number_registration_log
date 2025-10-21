import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import apiClient from '@/api'
import type {
  AssignNumberIn,
  AssignNumberOut,
  AssignedNumber,
  DocumentUpdatePayload,
} from '@/types/api'

const fetchAssignedNumbers = async (sessionId: string): Promise<AssignedNumber[]> => {
  console.warn(
    `API for fetching assigned numbers for session ${sessionId} does not exist. Using cache.`,
  )
  return []
}

const updateAssignedNumber = async ({
  id,
  payload,
}: {
  id: number
  payload: Partial<DocumentUpdatePayload>
}) => {
  const { data } = await apiClient.patch(`/documents/${id}`, payload)
  return { id, ...payload, ...data }
}

const assignNextNumber = async (payload: AssignNumberIn): Promise<AssignNumberOut> => {
  const { data } = await apiClient.post<AssignNumberOut>('/documents/assign-one', payload)
  return data
}

export function useNumberAssignment(sessionId: string) {
  const queryClient = useQueryClient()
  const queryKey = ['assignedNumbers', sessionId]

  const {
    data: assignedNumbers,
    isLoading: isLoadingAssigned,
    isError: isErrorAssigned,
  } = useQuery({
    queryKey,
    queryFn: () => fetchAssignedNumbers(sessionId),
    enabled: !!sessionId,
    initialData: [],
  })

  const {
    mutate: assignNumber,
    isPending: isAssigning,
    error: errorAssigning,
  } = useMutation<AssignNumberOut, Error, AssignNumberIn>({
    mutationFn: assignNextNumber,
    onSuccess: (response) => {
      queryClient.setQueryData<AssignedNumber[]>(queryKey, (oldData = []) => {
        const { created } = response
        const newEntry: AssignedNumber = {
          id: created.id,
          numeric: created.numeric,
          formatted_no: created.formatted_no,
          doc_name: created.doc_name,
          note: created.note,
        }
        return [...oldData, newEntry]
      })
    },
  })

  const { mutate: updateNumber, isPending: isUpdating } = useMutation({
    mutationFn: updateAssignedNumber,
    onSuccess: (updatedData) => {
      queryClient.setQueryData<AssignedNumber[]>(queryKey, (oldData = []) => {
        return oldData.map((item) =>
          item.id === updatedData.id ? { ...item, ...updatedData } : item,
        )
      })
    },
  })

  return {
    assignedNumbers,
    isLoadingAssigned,
    errorAssigning,
    assignNumber,
    isAssigning,
    isErrorAssigned,
    updateNumber,
    isUpdating,
  }
}
