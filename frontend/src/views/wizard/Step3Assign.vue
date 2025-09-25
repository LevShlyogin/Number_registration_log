<template>
  <v-container fluid class="pa-0">
    <!-- Верхняя панель: заголовок + сводка -->
    <v-sheet class="pa-3 border-b rounded-b-0 summary-bar">
      <div class="d-flex flex-wrap align-center justify-space-between gap-3">
        <h3 class="text-h6 font-weight-medium mb-0">Шаг 3: Назначение номеров</h3>

        <div class="d-flex flex-wrap gap-2 align-center">
          <v-chip v-if="selectedFreeNumber !== null" color="info" variant="tonal" size="small">
            Выбран: <strong class="ml-1">{{ selectedFreeNumber }}</strong>
          </v-chip>
          <v-chip v-else-if="nextFreeNumber" color="info" variant="tonal" size="small">
            Следующий: <strong class="ml-1">{{ nextFreeNumber }}</strong>
          </v-chip>
          <v-chip v-else color="grey" variant="tonal" size="small">Нет свободных</v-chip>
        </div>
      </div>
    </v-sheet>

    <v-row class="mt-2">
      <!-- Левая колонка: форма назначения -->
      <v-col cols="12" md="5">
        <v-card variant="outlined" class="rounded-lg" :elevation="0">
          <v-card-title class="text-subtitle-1 py-3"> Форма назначения </v-card-title>
          <v-divider></v-divider>

          <v-card-text class="pt-4">
            <v-form ref="formRef" @submit.prevent="handleAssign">
              <v-alert
                v-if="!nextFreeNumber && selectedFreeNumber === null"
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
                clearable
                hide-details="auto"
                placeholder="Начните вводить для поиска или введите новое"
                no-filter
                density="comfortable"
                class="mb-4"
                prepend-inner-icon="mdi-text-box"
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
                :disabled="isAssigning || (freeNumbers.length === 0 && selectedFreeNumber === null)"
                variant="filled"
                hide-details="auto"
                density="comfortable"
                auto-grow
                prepend-inner-icon="mdi-note-text"
                class="mb-4"
              />

              <v-autocomplete
                v-model="selectedFreeNumber"
                :items="freeNumbers"
                :disabled="isAssigning || freeNumbers.length === 0"
                :return-object="false"
                label="Выбор свободного номера"
                placeholder="Начните вводить номер..."
                clearable
                variant="outlined"
                hide-details="auto"
                density="comfortable"
                prepend-inner-icon="mdi-counter"
                class="mb-2"
              />

              <v-sheet
                v-if="selectedFreeNumber !== null || nextFreeNumber !== null"
                color="blue-lighten-5"
                class="d-flex align-center justify-space-between pa-3 rounded-lg mt-2"
              >
                <div class="d-flex align-center">
                  <v-icon color="primary" class="mr-2">mdi-counter</v-icon>
                  <div class="text-body-2">
                    <template v-if="selectedFreeNumber !== null">
                      Выбран номер:
                      <strong class="text-primary">{{ selectedFreeNumber }}</strong>
                    </template>
                    <template v-else>
                      Будет назначен номер:
                      <strong class="text-primary">{{ nextFreeNumber }}</strong>
                    </template>
                  </div>
                </div>
                <div class="d-flex align-center">
                  <v-btn
                    v-if="selectedFreeNumber !== null"
                    size="small"
                    variant="text"
                    @click="clearSelected"
                  >
                    ОТМЕНА
                  </v-btn>
                </div>
              </v-sheet>

              <div class="d-flex gap-2 mt-4">
                <v-btn
                  type="submit"
                  :loading="isAssigning"
                  :disabled="
                    !formData.doc_name || (selectedFreeNumber === null && nextFreeNumber === null)
                  "
                  color="primary"
                  variant="flat"
                  block
                >
                  <v-icon start icon="mdi-plus-box"></v-icon>
                  {{ selectedFreeNumber !== null ? 'Назначить выбранный' : 'Назначить следующий' }}
                </v-btn>

                <v-btn
                  type="button"
                  color="default"
                  variant="text"
                  :disabled="isAssigning"
                  @click="resetForm"
                >
                  Сбросить
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Правая колонка: списки номеров -->
      <v-col cols="12" md="7">
        <v-card variant="outlined" class="rounded-lg" :elevation="0">
          <v-tabs v-model="rightTab" density="comfortable" class="px-2">
            <v-tab value="free">
              <v-icon start size="18">mdi-checkbox-blank-circle-outline</v-icon>
              Свободные
              <v-chip size="x-small" class="ml-2" color="success" variant="tonal">
                {{ freeNumbers.length }}
              </v-chip>
            </v-tab>
            <v-tab value="assigned">
              <v-icon start size="18">mdi-checkbox-marked-circle</v-icon>
              Назначенные
              <v-chip size="x-small" class="ml-2" color="primary" variant="tonal">
                {{ assignedCount }}
              </v-chip>
            </v-tab>
          </v-tabs>

          <v-divider></v-divider>

          <v-window v-model="rightTab">
            <!-- Свободные номера -->
            <v-window-item value="free">
              <v-card-text>
                <div class="d-flex align-center gap-2 mb-2">
                  <v-text-field
                    v-model="searchFree"
                    placeholder="Фильтр по свободным номерам..."
                    prepend-inner-icon="mdi-magnify"
                    density="comfortable"
                    variant="outlined"
                    hide-details
                    clearable
                    class="flex-1-1"
                  />
                  <v-btn
                    v-if="selectedFreeNumber !== null"
                    size="small"
                    variant="text"
                    @click="clearSelected"
                  >
                    Снять выбор
                  </v-btn>
                </div>

                <v-sheet class="rounded-lg border pa-3" min-height="220">
                  <div
                    v-if="filteredFreeNumbers.length === 0"
                    class="d-flex justify-center align-center"
                    style="min-height: 200px"
                  >
                    <v-chip color="grey-lighten-2" size="small">Пусто</v-chip>
                  </div>

                  <div v-else>
                    <v-chip-group
                      v-model="selectedFreeNumber"
                      class="free-grid"
                      selected-class="selected-chip"
                      :multiple="false"
                      :mandatory="false"
                    >
                      <v-chip
                        v-for="num in filteredFreeNumbers"
                        :key="num"
                        :value="num"
                        label
                        size="small"
                        variant="tonal"
                        class="mb-2"
                        :aria-pressed="selectedFreeNumber === num"
                      >
                        {{ num }}
                      </v-chip>
                    </v-chip-group>
                  </div>
                </v-sheet>
              </v-card-text>
            </v-window-item>

            <!-- Назначенные номера -->
            <v-window-item value="assigned">
              <v-card-text>
                <div class="d-flex align-center justify-space-between mb-2">
                  <v-text-field
                    v-model="searchAssigned"
                    placeholder="Поиск по номеру или документу..."
                    prepend-inner-icon="mdi-magnify"
                    density="comfortable"
                    variant="outlined"
                    hide-details
                    clearable
                    class="flex-1-1"
                  />
                </div>

                <v-progress-linear
                  v-if="isLoadingAssigned"
                  indeterminate
                  height="2"
                  color="primary"
                  class="mb-2"
                />

                <v-data-table
                  :headers="assignedHeaders"
                  :items="filteredAssigned"
                  :items-per-page="10"
                  item-key="doc_no"
                  density="compact"
                  class="rounded-lg"
                  no-data-text="Пока пусто"
                  :loading="isLoadingAssigned"
                >
                  <template #[`item.doc_no`]="{ item }">
                    <span class="font-weight-bold">{{ item.doc_no }}</span>
                  </template>

                  <template #[`item.notes`]="{ item }">
                    <span class="text-medium-emphasis">{{ item.notes ?? '—' }}</span>
                  </template>

                  <template #[`item.actions`]="{ item }">
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="small"
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

    <!-- Навигация -->
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
import { useWizardStore } from '@/stores/wizard'
import { useNumberAssignment } from '@/composables/useNumberAssignment'
import { useDocNameSuggestions } from '@/composables/useSuggestions'
import EditAssignedDialog from '@/components/wizard/EditAssignedDialog.vue'
import type { AssignedNumber, DocumentUpdatePayload } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'
import { VForm } from 'vuetify/components'

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

// counts and lists
const assignedCount = computed(() => assignedNumbers.value?.length ?? 0)

const freeNumbers = computed<number[]>(() => {
  const assignedSet = new Set(assignedNumbers.value?.map((item) => item.doc_no) ?? [])
  return wizardStore.reservedNumbers.filter((num) => !assignedSet.has(num))
})

const nextFreeNumber = computed<number | null>(() => {
  return freeNumbers.value.length > 0 ? freeNumbers.value[0] : null
})

// Ручной выбор свободного номера
const selectedFreeNumber = ref<number | null>(null)
const searchFree = ref('')

const filteredFreeNumbers = computed<number[]>(() => {
  const list = freeNumbers.value
  const q = searchFree.value?.toString().trim()
  if (!q) return list
  return list.filter((n) => n.toString().includes(q))
})

// сбрасываем выбранный номер, если он исчез из списка
watch(freeNumbers, (list) => {
  if (selectedFreeNumber.value !== null && !list.includes(selectedFreeNumber.value)) {
    selectedFreeNumber.value = null
  }
})

// поиск по назначенным
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
  { title: '№', key: 'doc_no', sortable: true, width: 100 },
  { title: 'Документ', key: 'doc_name', sortable: true },
  { title: 'Примечание', key: 'notes', sortable: false },
  { title: '', key: 'actions', sortable: false, align: 'end', width: 72 },
] as const

async function handleAssign() {
  const { valid } = await formRef.value.validate()
  const numberToAssign = selectedFreeNumber.value ?? nextFreeNumber.value

  if (valid && wizardStore.currentSessionId && numberToAssign !== null) {
    assignNumber(
      {
        data: {
          session_id: wizardStore.currentSessionId,
          doc_name: formData.doc_name.trim(),
          notes: formData.notes,
        },
        nextNumberToAssign: numberToAssign,
      },
      {
        onSuccess: () => {
          resetForm()
          clearSelected()
          suggestions.searchQuery.value = ''
          rightTab.value = 'assigned'
        },
      },
    )
  }
}

function resetForm() {
  formRef.value?.reset()
  formData.doc_name = ''
  formData.notes = ''
}

function clearSelected() {
  selectedFreeNumber.value = null
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

<style scoped>
.summary-bar {
  position: sticky;
  top: 0;
  z-index: 2;
  background: rgb(var(--v-theme-surface));
}

.free-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(72px, 1fr));
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}
</style>
