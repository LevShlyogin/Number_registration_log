<template>
  <v-container fluid class="pa-0">
    <h3 class="text-h6 font-weight-medium mb-2">Шаг 3: Назначение номеров</h3>
    <p class="text-body-1 mb-6 text-grey">
      Сессия ID: <strong>{{ sessionId }}</strong>
    </p>

    <v-row>
      <v-col cols="12" md="5">
        <h4 class="text-subtitle-1 font-weight-medium mb-3">Форма назначения</h4>
        <v-form ref="formRef" @submit.prevent="handleAssign">
          <p class="text-body-2 mb-2">
            Свободно номеров: <strong class="text-success">{{ freeNumbers.length }}</strong>
          </p>
          <p class="text-body-2 text-grey mb-4">
            Следующий номер:
            <strong v-if="nextFreeNumber" class="text-primary">{{ nextFreeNumber }}</strong>
            <em v-else>нет</em>
          </p>

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
            hide-details="auto"
            placeholder="Начните вводить для поиска или введите новое"
            no-filter
            clearable
          >
            <template #no-data>
              <v-list-item>
                <v-list-item-title> Совпадений не найдено </v-list-item-title>
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
            class="mt-4"
          ></v-textarea>

          <v-btn
            type="submit"
            :loading="isAssigning"
            :disabled="freeNumbers.length === 0"
            color="primary"
            variant="flat"
            block
            class="mt-4"
          >
            <v-icon start icon="mdi-plus-box"></v-icon>
            Назначить следующий
          </v-btn>

          <v-alert v-if="isErrorAssigning" type="error" variant="tonal" class="mt-4">
            {{ (errorAssigning as Error).message }}
          </v-alert>
        </v-form>
      </v-col>

      <v-col cols="12" md="7">
        <v-row>
          <v-col cols="12" sm="6">
            <h4 class="text-subtitle-1 font-weight-medium mb-3">Свободные номера</h4>
            <v-sheet class="border pa-2" rounded="lg" min-height="150">
              <v-chip v-if="freeNumbers.length === 0" color="grey-lighten-2" size="small"
                >Пусто</v-chip
              >
              <v-chip-group v-else>
                <v-chip v-for="num in freeNumbers" :key="num" label size="small">
                  {{ num }}
                </v-chip>
              </v-chip-group>
            </v-sheet>
          </v-col>

          <v-col cols="12" sm="6">
            <v-card variant="outlined" height="100%">
              <v-card-title>Назначенные номера</v-card-title>
              <v-progress-linear v-if="isLoadingAssigned" indeterminate></v-progress-linear>
              <v-card-text>
                <v-list v-if="assignedNumbers && assignedNumbers.length > 0" density="compact">
                  <v-list-item
                    v-for="item in assignedNumbers"
                    :key="item.doc_no"
                    :title="String(item.doc_no)"
                    :subtitle="item.doc_name"
                  >
                    <!-- --- НОВАЯ КНОПКА РЕДАКТИРОВАНИЯ --- -->
                    <template #append>
                      <v-btn
                        icon="mdi-pencil"
                        variant="text"
                        size="x-small"
                        @click="openEditDialog(item)"
                      ></v-btn>
                    </template>
                  </v-list-item>
                </v-list>
                <v-chip v-else color="grey" size="small">Еще нет назначенных номеров</v-chip>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
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
  </v-container>
  <edit-assigned-dialog
    v-model="isEditDialogOpen"
    :item="selectedItemForEdit"
    :loading="isUpdating"
    @save="handleUpdate"
  />
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWizardStore } from '@/stores/wizard'
import { useNumberAssignment } from '@/composables/useNumberAssignment'
import { useDocNameSuggestions } from '@/composables/useSuggestions'
import EditAssignedDialog from '@/components/wizard/EditAssignedDialog.vue' // Импорт
import type { AssignedNumber, DocumentUpdatePayload } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'

const suggestions = useDocNameSuggestions()
const notifier = useNotifier()

const props = defineProps<{
  sessionId: string
}>()

const router = useRouter()
const wizardStore = useWizardStore()
const {
  assignedNumbers,
  isLoadingAssigned,
  isErrorAssigning,
  errorAssigning,
  assignNumber,
  isAssigning,
  updateNumber,
  isUpdating,
} = useNumberAssignment(props.sessionId)

const isEditDialogOpen = ref(false)
const selectedItemForEdit = ref<AssignedNumber | null>(null)

const formRef = ref<any>(null)
const formData = reactive({
  doc_name: '',
  notes: '',
})
const rules = {
  required: (value: string) => (!!value && value.trim().length > 0) || 'Это поле обязательно.',
}

const freeNumbers = computed(() => {
  const assignedSet = new Set(assignedNumbers.value?.map((item) => item.doc_no) ?? [])
  return wizardStore.reservedNumbers.filter((num) => !assignedSet.has(num))
})

const nextFreeNumber = computed(() => {
  return freeNumbers.value.length > 0 ? freeNumbers.value[0] : null
})

async function handleAssign() {
  const { valid } = await formRef.value.validate()

  if (valid && wizardStore.currentSessionId && nextFreeNumber.value !== null) {
    assignNumber(
      {
        data: {
          session_id: wizardStore.currentSessionId,
          doc_name: formData.doc_name.trim(),
          notes: formData.notes,
        },
        nextNumberToAssign: nextFreeNumber.value,
      },
      {
        onSuccess: () => {
          formRef.value.reset()
          suggestions.searchQuery.value = ''
        },
      },
    )
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
        isEditDialogOpen.value = false // Закрываем диалог
        notifier.success('Запись успешно обновлена!')
      },
      onError: (e) => {
        notifier.error(`Ошибка обновления: ${(e as Error).message}`)
      },
    },
  )
}

function goBack() {
  router.back()
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
