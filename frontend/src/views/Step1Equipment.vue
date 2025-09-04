<script setup lang="ts">
import { useWizardStore } from '@/stores/wizard'
import { useRouter } from 'vue-router'

const wizardStore = useWizardStore()
const router = useRouter()

function onEquipmentSelected(equipmentId: number) {
  wizardStore.setEquipment(equipmentId)
  // Переходим на следующий шаг, передавая ID в URL
  router.push({ name: 'wizard-reserve', params: { equipmentId: equipmentId } })
}
</script>
