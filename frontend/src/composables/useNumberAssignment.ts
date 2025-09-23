import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import type {
  AssignNumberIn,
  AssignNumberOut,
  AssignedNumber,
  DocumentUpdatePayload,
} from '@/types/api'

// --- API-функции ---

const fetchAssignedNumbers = async (sessionId: string): Promise<AssignedNumber[]> => {
  console.log('Fetching assigned numbers for session:', sessionId)
  await new Promise((resolve) => setTimeout(resolve, 400))
  return []
}

const updateAssignedNumber = async ({
  id,
  payload,
}: {
  id: number
  payload: Partial<DocumentUpdatePayload>
}) => {
  console.log(`Updating assigned number ${id} with:`, payload)
  await new Promise((resolve) => setTimeout(resolve, 500))
  return { ...payload, doc_no: id }
}

// Тип для полезной нагрузки мутации
interface AssignNumberPayload {
  data: AssignNumberIn
  nextNumberToAssign: number
}

// Назначение следующего свободного номера
const assignNextNumber = async (payload: AssignNumberPayload): Promise<AssignNumberOut> => {
  const { data, nextNumberToAssign } = payload

  // --- ЗАГЛУШКА API ---
  console.log('Assigning next number with payload:', data, 'and number:', nextNumberToAssign)
  await new Promise((resolve) => setTimeout(resolve, 600))

  const mockResponse: AssignNumberOut = {
    session_id: data.session_id,
    doc_no: nextNumberToAssign,
    doc_name: data.doc_name,
    created: new Date().toISOString(),
    user: 'yuaalekseeva',
  }
  console.log('Mock response for assignment:', mockResponse)
  return mockResponse
  // --- КОНЕЦ ЗАГЛУШКИ ---
}

export function useNumberAssignment(sessionId: string) {
  const queryClient = useQueryClient()
  const queryKey = ['assignedNumbers', sessionId]

  // Query для получения списка назначенных номеров
  const {
    data: assignedNumbers,
    isLoading: isLoadingAssigned,
    isError: isErrorAssigned,
  } = useQuery({
    queryKey,
    queryFn: () => fetchAssignedNumbers(sessionId),
    enabled: !!sessionId,
  })

  const {
    mutate: assignNumber,
    isPending: isAssigning,
    isError: isErrorAssigning,
    error: errorAssigning,
  } = useMutation<AssignNumberOut, Error, AssignNumberPayload>({
    mutationFn: assignNextNumber,
    onSuccess: (newlyAssignedNumber) => {
      queryClient.setQueryData<AssignedNumber[]>(queryKey, (oldData) => {
        const newEntry: AssignedNumber = {
          doc_no: newlyAssignedNumber.doc_no,
          doc_name: newlyAssignedNumber.doc_name,
        }
        return oldData ? [...oldData, newEntry] : [newEntry]
      })
    },
  })

  const { mutate: updateNumber, isPending: isUpdating } = useMutation({
    mutationFn: updateAssignedNumber,
    onSuccess: (updatedData) => {
      queryClient.setQueryData<AssignedNumber[]>(queryKey, (oldData) => {
        return (
          oldData?.map((item) =>
            item.doc_no === updatedData.doc_no
              ? { ...item, doc_name: updatedData.doc_name! }
              : item,
          ) ?? []
        )
      })
    },
  })

  return {
    assignedNumbers,
    isLoadingAssigned,
    isErrorAssigning,
    errorAssigning,
    assignNumber,
    isAssigning,
    isErrorAssigned,
    updateNumber,
    isUpdating,
  }
}
