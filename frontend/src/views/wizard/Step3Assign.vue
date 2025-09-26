<template>
  <v-container fluid class="pa-0">
    <v-sheet class="pa-3 border-b rounded-b-0 summary-bar">
      <div class="d-flex flex-wrap align-center justify-space-between gap-3">
        <h3 class="text-h6 font-weight-medium mb-0">Шаг 3: Назначение номеров</h3>

        <div class="d-flex flex-wrap gap-2 align-center">
          <v-chip
            color="success"
            variant="tonal"
            size="small"
            prepend-icon="mdi-checkbox-blank-circle-outline"
          >
            Свободно: <strong class="ml-1">{{ freeNumbers.length }}</strong>
          </v-chip>
          <v-chip
            color="primary"
            variant="tonal"
            size="small"
            prepend-icon="mdi-checkbox-marked-circle-outline"
          >
            Назначено: <strong class="ml-1">{{ assignedCount }}</strong>
          </v-chip>
          <v-chip
            v-if="numberToAssign"
            color="info"
            variant="tonal"
            size="small"
            prepend-icon="mdi-target-account"
          >
            К назначению: <strong class="ml-1">{{ numberToAssign }}</strong>
          </v-chip>
          <v-chip v-else color="grey" variant="tonal" size="small">Нет свободных</v-chip>
        </div>
      </div>
    </v-sheet>

    <v-row class="mt-2">
      <v-col cols="12" md="5">
        <v-card flat class="border rounded-lg">
          <v-card-title class="text-subtitle-1 py-3"> Форма назначения </v-card-title>
          <v-divider></v-divider>

          <v-card-text class="pt-4">
            <v-form ref="formRef" @submit.prevent="handleAssign">
              <v-alert
                v-if="freeNumbers.length === 0"
                type="warning"
                variant="tonal"
                density="comfortable"
                class="mb-4"
              >
                Свободных номеров нет — назначение недоступно.
              </v-alert>

              <v-combobox
                v-model="formData.doc_name"
                v-model:search="suggestions.searchQuery.value"
                :items="suggestions.suggestions.value || []"
                :loading="suggestions.isLoading.value"
                label="Наименование документа"
                :rules="[rules.required]"
                :disabled="isAssigning || freeNumbers.length === 0"
                variant="filled"
                flat
                clearable
                hide-details="auto"
                placeholder="Начните вводить для поиска или введите новое"
                no-filter
                density="comfortable"
                class="mb-4"
              >
                <template #no-data>
                  <v-list-item>
                    <v-list-item-title class="text-caption">
                      Ничего не найдено — можно использовать новое наименование.
                    </v-list-item-title>
                  </v-list-item>
                </template>
              </v-combobox>

              <v-textarea
                v-model="formData.notes"
                label="Примечание"
                rows="3"
                :disabled="isAssigning || freeNumbers.length === 0"
                variant="filled"
                flat
                hide-details="auto"
                density="comfortable"
                auto-grow
                class="mb-4"
              />

              <v-autocomplete
                v-model="selectedFreeNumber"
                :items="freeNumbers"
                :disabled="isAssigning || freeNumbers.length === 0"
                label="Выбрать конкретный свободный номер"
                placeholder="Необязательно"
                clearable
                variant="outlined"
                hide-details="auto"
                density="comfortable"
                class="mb-2"
              />

              <v-btn
                type="submit"
                :loading="isAssigning"
                :disabled="!formData.doc_name || !numberToAssign"
                color="primary"
                variant="flat"
                block
                size="large"
                class="mt-4"
              >
                <v-icon start icon="mdi-plus-box"></v-icon>
                Назначить номер {{ numberToAssign }}
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="7">
        <v-card flat class="border rounded-lg">
          <v-tabs v-model="rightTab" density="comfortable" class="px-2">
            <v-tab value="free">Свободные</v-tab>
            <v-tab value="assigned">Назначенные</v-tab>
          </v-tabs>
          <v-divider></v-divider>

          <v-window v-model="rightTab">
            <v-window-item value="free">
              <v-card-text>
                <v-text-field
                  v-model="searchFree"
                  placeholder="Фильтр по свободным номерам..."
                  prepend-inner-icon="mdi-magnify"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  clearable
                  class="mb-2"
                />
                <v-sheet class="rounded-lg border pa-3 free-grid" min-height="220">
                  <div v-if="filteredFreeNumbers.length === 0" class="empty-state">
                    <v-chip color="grey-lighten-2" size="small">Пусто</v-chip>
                  </div>
                  <v-chip
                    v-for="num in filteredFreeNumbers"
                    :key="num"
                    label
                    size="small"
                    :variant="selectedFreeNumber === num ? 'flat' : 'tonal'"
                    :color="selectedFreeNumber === num ? 'primary' : 'default'"
                    @click="toggleSelectFreeNumber(num)"
                    class="ma-1"
                  >
                    {{ num }}
                  </v-chip>
                </v-sheet>
              </v-card-text>
            </v-window-item>

            <v-window-item value="assigned">
              <v-card-text>
                <v-text-field
                  v-model="searchAssigned"
                  placeholder="Поиск по номеру или документу..."
                  prepend-inner-icon="mdi-magnify"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  clearable
                  class="mb-2"
                />
                <v-data-table
                  :headers="assignedHeaders"
                  :items="filteredAssigned"
                  :items-per-page="-1"
                  item-value="doc_no"
                  density="compact"
                  no-data-text="Пока пусто"
                  :loading="isLoadingAssigned"
                  fixed-header
                  height="320px"
                  class="assigned-table"
                >
                  <template #[`item.doc_name`]="{ item }">
                    <v-tooltip :text="item.doc_name" location="top">
                      <template #activator="{ props }">
                        <div v-bind="props" class="truncate-text">
                          {{ item.doc_name }}
                        </div>
                      </template>
                    </v-tooltip>
                  </template>

                  <template #[`item.notes`]="{ item }">
                    <v-tooltip :text="item.notes" location="top" v-if="item.notes">
                      <template #activator="{ props }">
                        <div v-bind="props" class="truncate-text">
                          {{ item.notes }}
                        </div>
                      </template>
                    </v-tooltip>
                    <span v-else class="text-medium-emphasis">—</span>
                  </template>

                  <template #[`item.actions`]="{ item }">
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="x-small"
                      @click="openEditDialog(item)"
                      :aria-label="'Редактировать ' + item.doc_no"
                    />
                  </template>

                  <template #bottom></template>
                </v-data-table>
              </v-card-text>
            </v-window-item>
          </v-window>
        </v-card>
      </v-col>
    </v-row>

    <v-divider class="my-6"></v-divider>

    <div class="d-flex justify-space-between align-center">
      <v-btn @click="goBack" variant="text">
        <v-icon start icon="mdi-arrow-left"></v-icon>
        Назад
      </v-btn>

      <v-alert
        v-if="freeNumbers.length === 0 && wizardStore.hasActiveSession"
        type="warning"
        variant="tonal"
        density="compact"
        class="text-caption"
      >
        Все зарезервированные номера назначены.
      </v-alert>

      <v-btn @click="complete" color="success" size="large" variant="flat">
        <v-icon start icon="mdi-check-all"></v-icon>
        Завершить
      </v-btn>
    </div>

    <edit-assigned-dialog
      v-model="isEditDialogOpen"
      :item="selectedItemForEdit"
      :loading="isUpdating"
      @save="handleUpdate"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { VForm } from 'vuetify/components'
import { useWizardStore } from '@/stores/wizard'
import { useNumberAssignment } from '@/composables/useNumberAssignment'
import { useDocNameSuggestions } from '@/composables/useSuggestions'
import EditAssignedDialog from '@/components/wizard/EditAssignedDialog.vue'
import type { AssignedNumber, DocumentUpdatePayload } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'

const suggestions = useDocNameSuggestions()
const notifier = useNotifier()

const props = defineProps<{
  sessionId: string
}>()

const router = useRouter()
const wizardStore = useWizardStore()
const { assignedNumbers, isLoadingAssigned, assignNumber, isAssigning, updateNumber, isUpdating } =
  useNumberAssignment(props.sessionId)

const isEditDialogOpen = ref(false)
const selectedItemForEdit = ref<AssignedNumber | null>(null)
const rightTab = ref<'free' | 'assigned'>('free')

const formRef = ref<InstanceType<typeof VForm> | null>(null)
const formData = reactive({
  doc_name: '',
  notes: '',
})

const rules = {
  required: (value: string) => (!!value && value.trim().length > 0) || 'Это поле обязательно.',
}

const assignedCount = computed(() => assignedNumbers.value?.length ?? 0)

const freeNumbers = computed<number[]>(() => {
  const assignedSet = new Set(assignedNumbers.value?.map((item) => item.doc_no) ?? [])
  return wizardStore.reservedNumbers.filter((num) => !assignedSet.has(num))
})

const nextFreeNumber = computed<number | null>(() => {
  return freeNumbers.value.length > 0 ? freeNumbers.value[0] : null
})

const selectedFreeNumber = ref<number | null>(null)
const searchFree = ref('')

const filteredFreeNumbers = computed<number[]>(() => {
  const list = freeNumbers.value
  const q = searchFree.value?.toString().trim()
  if (!q) return list
  return list.filter((n) => n.toString().includes(q))
})

watch(freeNumbers, (list) => {
  if (selectedFreeNumber.value !== null && !list.includes(selectedFreeNumber.value)) {
    selectedFreeNumber.value = null
  }
})

const searchAssigned = ref('')

const filteredAssigned = computed<AssignedNumber[]>(() => {
  const list = assignedNumbers.value ?? []
  const q = searchAssigned.value?.toString().trim().toLowerCase()
  if (!q) return list
  return list.filter((item) => {
    const haystack = [item.doc_no?.toString() ?? '', item.doc_name ?? '', item.notes ?? '']
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

const assignedHeaders = [
  { title: '№', key: 'doc_no', sortable: true, width: '20%' },
  { title: 'Документ', key: 'doc_name', sortable: true, width: '40%' },
  { title: 'Примечание', key: 'notes', sortable: false, width: '25%' },
  { title: 'Ред.', key: 'actions', sortable: false, align: 'end', width: '15%' },
] as const

const numberToAssign = computed(() => selectedFreeNumber.value ?? nextFreeNumber.value)

async function handleAssign() {
  if (!formRef.value) return
  const { valid } = await formRef.value.validate()

  if (valid && wizardStore.currentSessionId && numberToAssign.value !== null) {
    assignNumber(
      {
        data: {
          session_id: wizardStore.currentSessionId,
          doc_name: formData.doc_name.trim(),
          notes: formData.notes,
        },
        nextNumberToAssign: numberToAssign.value,
      },
      {
        onSuccess: () => {
          resetForm()
          selectedFreeNumber.value = null // También limpiar el número seleccionado manualmente
          suggestions.searchQuery.value = ''
          rightTab.value = 'assigned'
        },
      },
    )
  }
}

function resetForm() {
  formRef.value?.reset()
}
function toggleSelectFreeNumber(num: number) {
  if (selectedFreeNumber.value === num) {
    selectedFreeNumber.value = null
  } else {
    selectedFreeNumber.value = num
  }
}

function openEditDialog(item: AssignedNumber) {
  selectedItemForEdit.value = item
  isEditDialogOpen.value = true
}

function handleUpdate({ id, payload }: { id: number; payload: Partial<DocumentUpdatePayload> }) {
  updateNumber(
    { id, payload },
    {
      onSuccess: () => {
        isEditDialogOpen.value = false
        notifier.success('Запись успешно обновлена!')
      },
      onError: (e) => {
        notifier.error(`Ошибка обновления: ${(e as Error).message}`)
      },
    },
  )
}

function goBack() {
  if (wizardStore.selectedEquipmentId) {
    router.push({
      name: 'wizard-reserve',
      params: { equipmentId: wizardStore.selectedEquipmentId },
    })
  } else {
    router.push({ name: 'wizard-equipment' })
  }
}

function complete() {
  const sessionIdToReport = wizardStore.currentSessionId
  wizardStore.reset()
  router.push({
    name: 'reports',
    state: { lastSessionId: sessionIdToReport },
  })
}
</script>

<style>
.assigned-table .v-table__wrapper > table {
  table-layout: fixed;
  width: 100%;
}

.truncate-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<style scoped>
.summary-bar {
  position: sticky;
  top: 64px;
  z-index: 2;
  background: rgb(var(--v-theme-surface));
}

.free-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
  align-content: start;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 180px;
}
</style>
