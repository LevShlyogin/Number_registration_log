<template>
  <v-container fluid class="pa-0">
    <!-- Шапка со статусом -->
    <v-sheet class="pa-3 border-b rounded-b-0 summary-bar" color="surface">
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
        </div>
      </div>
    </v-sheet>

    <v-row class="mt-2">
      <!-- Левая колонка: Форма назначения -->
      <v-col cols="12" md="5">
        <v-card flat class="border rounded-lg">
          <v-card-title class="text-subtitle-1 py-3"> Форма назначения </v-card-title>
          <v-divider></v-divider>

          <v-card-text class="pt-4">
            <v-form ref="formRef" @submit.prevent="handleAssign">
              <v-alert
                v-if="!numberToAssign"
                type="info"
                variant="tonal"
                density="comfortable"
                class="mb-4"
              >
                Выберите свободный номер из списка справа.
              </v-alert>

              <v-combobox
                v-model="formData.doc_name"
                class="doc-name-combobox mb-4"
                v-model:search="suggestions.searchQuery.value"
                :items="suggestions.suggestions.value || []"
                :loading="suggestions.isLoading.value"
                label="Наименование документа"
                :rules="[rules.required]"
                variant="filled"
                flat
                clearable
                hide-details="auto"
                placeholder="Начните вводить или введите новое"
                no-filter
                density="comfortable"
              />
              <v-textarea
                v-model="formData.note"
                label="Примечание"
                rows="3"
                variant="filled"
                flat
                hide-details="auto"
                density="comfortable"
                auto-grow
                class="mb-4"
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

      <!-- Правая колонка: Списки номеров -->
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
                <v-sheet class="rounded-lg border pa-3 free-grid" min-height="220">
                  <div v-if="freeNumbers.length === 0" class="empty-state">
                    <v-chip color="grey-lighten-2" size="small">Пусто</v-chip>
                  </div>
                  <v-chip
                    v-for="num in freeNumbers"
                    :key="num"
                    label
                    size="small"
                    class="ma-1 number-chip"
                    :class="{ 'golden-chip': num % 100 === 0 }"
                    :variant="selectedFreeNumber === num ? 'flat' : 'tonal'"
                    :color="selectedFreeNumber === num ? 'primary' : undefined"
                    @click="toggleSelectFreeNumber(num)"
                  >
                    {{ num }}
                  </v-chip>
                </v-sheet>
              </v-card-text>
            </v-window-item>
            <v-window-item value="assigned">
              <v-card-text>
                <v-data-table
                  :headers="assignedHeaders"
                  :items="assignedNumbers || []"
                  :items-per-page="-1"
                  item-value="id"
                  density="compact"
                  no-data-text="Пока пусто"
                  :loading="isLoadingAssigned"
                  fixed-header
                  height="320px"
                  class="assigned-table"
                >
                  <template #[`item.formatted_no`]="{ item }">
                    <v-chip size="small" :class="{ 'golden-chip': item.numeric % 100 === 0 }">{{
                      item.formatted_no
                    }}</v-chip>
                  </template>
                  <template #[`item.doc_name`]="{ item }">
                    <div class="truncate-text">{{ item.doc_name }}</div>
                  </template>
                  <template #[`item.note`]="{ item }">
                    <div v-if="item.note" class="truncate-text">{{ item.note }}</div>
                    <span v-else class="text-medium-emphasis">—</span>
                  </template>
                  <template #[`item.actions`]="{ item }">
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="x-small"
                      @click="openEditDialog(item)"
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

    <!-- Навигация -->
    <v-divider class="my-6"></v-divider>
    <div class="d-flex justify-space-between align-center">
      <v-btn @click="goBack" variant="text">
        <v-icon start icon="mdi-arrow-left"></v-icon> Назад
      </v-btn>
      <v-btn @click="complete" color="success" size="large" variant="flat">
        <v-icon start icon="mdi-check-all"></v-icon> Завершить
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
import { AxiosError } from 'axios'

const props = defineProps<{ sessionId: string }>()
const router = useRouter()
const wizardStore = useWizardStore()
const { assignedNumbers, isLoadingAssigned, assignNumber, isAssigning, updateNumber, isUpdating } =
  useNumberAssignment(props.sessionId)
const suggestions = useDocNameSuggestions()
const notifier = useNotifier()

const formRef = ref<InstanceType<typeof VForm> | null>(null)
const formData = reactive({ doc_name: '', note: '' })
const rightTab = ref<'free' | 'assigned'>('free')
const selectedFreeNumber = ref<number | null>(null)
const isEditDialogOpen = ref(false)
const selectedItemForEdit = ref<AssignedNumber | null>(null)

const rules = { required: (v: string) => (!!v && v.trim().length > 0) || 'Обязательно.' }

const assignedCount = computed(() => assignedNumbers.value?.length ?? 0)
const freeNumbers = computed<number[]>(() => {
  const assignedSet = new Set(assignedNumbers.value?.map((item) => item.numeric) ?? [])
  return wizardStore.reservedNumbers.filter((num) => !assignedSet.has(num))
})

const numberToAssign = computed(() => selectedFreeNumber.value)

watch(freeNumbers, () => {
  selectedFreeNumber.value = null
})

function toggleSelectFreeNumber(num: number) {
  selectedFreeNumber.value = selectedFreeNumber.value === num ? null : num
}

async function handleAssign() {
  if (!formRef.value) return
  const { valid } = await formRef.value.validate()
  if (valid && wizardStore.currentSessionId && numberToAssign.value) {
    const payload = {
      session_id: wizardStore.currentSessionId,
      doc_name: formData.doc_name.trim(),
      note: formData.note ? formData.note.trim() : null,
      numeric: numberToAssign.value,
    }
    assignNumber(payload, {
      onSuccess: (response) => {
        notifier.success(`Номер ${response.created.formatted_no} назначен!`)
        formRef.value?.reset()
        rightTab.value = 'assigned'
      },
      onError: (error: unknown) => {
        let message = 'Произошла неизвестная ошибка'
        if (error instanceof AxiosError && error.response?.data?.detail) {
          message = error.response.data.detail
        } else if (error instanceof Error) {
          message = error.message
        }
        notifier.error(`Ошибка: ${message}`)
      },
    })
  }
}

function openEditDialog(item: AssignedNumber) {
  selectedItemForEdit.value = { ...item }
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
      onError: (error: unknown) => {
        let message = 'Произошла неизвестная ошибка'
        if (error instanceof AxiosError && error.response?.data?.detail) {
          message = error.response.data.detail
        } else if (error instanceof Error) {
          message = error.message
        }
        notifier.error(`Ошибка обновления: ${message}`)
      },
    },
  )
}

function goBack() {
  router.back()
}
function complete() {
  wizardStore.reset()
  router.push({ name: 'reports' })
}

const assignedHeaders = [
  { title: '№', key: 'formatted_no', sortable: true, width: '20%' },
  { title: 'Документ', key: 'doc_name', sortable: true, width: '40%' },
  { title: 'Примечание', key: 'note', sortable: false, width: '25%' },
  { title: 'Ред.', key: 'actions', sortable: false, align: 'end', width: '15%' },
] as const
</script>

<style scoped>
.summary-bar {
  position: sticky;
  top: 64px;
  z-index: 2;
}
.doc-name-combobox :deep(input) {
  cursor: text !important;
}
.free-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  max-height: 320px;
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
.assigned-table .v-table__wrapper > table {
  table-layout: fixed;
  width: 100%;
}
.truncate-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.number-chip {
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.golden-chip {
  color: #b58700;
  border-color: currentColor;
}
</style>
