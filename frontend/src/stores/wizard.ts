import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useWizardStore = defineStore('wizard', () => {
  // --- State ---
  const selectedEquipmentId = ref<number | null>(null)
  const currentSessionId = ref<string | null>(null)
  const reservedNumbers = ref<number[]>([])

  // --- Getters (computed properties) ---
  const hasSelectedEquipment = computed(() => selectedEquipmentId.value !== null)
  const hasActiveSession = computed(() => currentSessionId.value !== null)

  // --- Actions ---
  function setEquipment(equipmentId: number) {
    console.log('Wizard Store: set equipment ID to', equipmentId)
    selectedEquipmentId.value = equipmentId
    // При выборе нового оборудования сбрасываем сессию
    currentSessionId.value = null
    reservedNumbers.value = []
  }

  function setSession(sessionId: string, numbers: number[]) {
    console.log('Wizard Store: set session ID to', sessionId)
    currentSessionId.value = sessionId
    reservedNumbers.value = numbers
  }

  function reset() {
    console.log('Wizard Store: resetting state')
    selectedEquipmentId.value = null
    currentSessionId.value = null
    reservedNumbers.value = []
  }

  return {
    // State
    selectedEquipmentId,
    currentSessionId,
    reservedNumbers,
    // Getters
    hasSelectedEquipment,
    hasActiveSession,
    // Actions
    setEquipment,
    setSession,
    reset,
  }
})
