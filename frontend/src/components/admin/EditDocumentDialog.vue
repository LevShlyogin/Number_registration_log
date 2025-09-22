<template>
  <v-dialog v-model="dialog" persistent max-width="800px">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Редактирование документа №{{ documentData?.doc_no }}</span>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" variant="text" @click="close"></v-btn>
      </v-card-title>
      <v-divider></v-divider>

      <v-form ref="formRef">
        <v-card-text style="max-height: 70vh; overflow-y: auto">
          <v-container>
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Данные документа</h3>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.doc_name"
                  label="Наименование документа"
                  :rules="[rules.required]"
                  required
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.note"
                  label="Примечание"
                  rows="2"
                  variant="outlined"
                  density="compact"
                ></v-textarea>
              </v-col>
            </v-row>
            <v-divider class="my-4"></v-divider>
            <h3 class="text-subtitle-1 font-weight-bold mb-3">Данные оборудования</h3>
            <v-row>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.eq_type"
                  label="Тип оборудования"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.station_object"
                  label="Станция/Объект"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.station_no"
                  label="№ станционный"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.factory_no"
                  label="№ заводской"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.order_no"
                  label="№ заказа"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  v-model="formData.label"
                  label="Маркировка"
                  variant="outlined"
                  density="compact"
                ></v-text-field
              ></v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-form>

      <v-divider></v-divider>
      <v-card-actions class="pa-4">
        <v-chip size="small" prepend-icon="mdi-account-outline">
          Пользователь: {{ documentData?.username }}
        </v-chip>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="close">Отмена</v-btn>
        <v-btn color="primary" variant="flat" @click="save" :loading="isSaving">
          Сохранить изменения
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, reactive, computed } from 'vue'
import type { AdminDocumentRow, DocumentUpdatePayload } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'

const props = defineProps<{
  document: AdminDocumentRow | null
}>()

const emit = defineEmits(['success'])
const dialog = defineModel<boolean>()
const formRef = ref<any>(null)
const isSaving = ref(false)
const notifier = useNotifier()

// Используем reactive для данных формы
const formData = reactive<DocumentUpdatePayload>({})

// Синхронизируем данные формы с пропсом `document`, когда диалог открывается
watch(
  () => props.document,
  (newDoc) => {
    if (newDoc) {
      Object.assign(formData, {
        doc_name: newDoc.doc_name,
        note: newDoc.note,
        eq_type: newDoc.eq_type,
        station_object: newDoc.station_object,
        station_no: newDoc.station_no,
        factory_no: newDoc.factory_no,
        order_no: newDoc.order_no,
        label: newDoc.label,
      })
    }
  },
)

const rules = {
  required: (value: string) => !!value || 'Это поле обязательно.',
}

async function save() {
  if (!props.document) return;
  const { valid } = await formRef.value.validate();
  if (valid) {
    isSaving.value = true;
    console.log('Saving document...', { id: props.document.id, payload: formData });
    await new Promise(resolve => setTimeout(resolve, 800)); // Имитация
    isSaving.value = false;
    notifier.success(`Данные для документа №${props.document.doc_no} сохранены!`);
    emit('success', { id: props.document.id, payload: formData });
  }
}

function close() {
  dialog.value = false
}

// Преобразуем `document` в `computed`, чтобы избежать прямого использования пропса в шаблоне
const documentData = computed(() => props.document)
</script>
