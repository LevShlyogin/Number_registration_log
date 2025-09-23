<template>
  <v-dialog v-model="dialog" persistent max-width="500px">
    <v-card>
      <v-card-title>Редактирование записи №{{ itemData?.doc_no }}</v-card-title>
      <v-card-text>
        <v-form ref="formRef">
          <v-text-field
            v-model="formData.doc_name"
            label="Наименование документа"
            :rules="[(v) => !!v || 'Обязательно']"
            class="mb-2"
          ></v-text-field>
          <v-textarea v-model="formData.notes" label="Примечание" rows="2"></v-textarea>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="close">Отмена</v-btn>
        <v-btn color="primary" variant="flat" @click="save" :loading="loading">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import type { AssignedNumber } from '@/types/api'

const props = defineProps<{
  item: AssignedNumber | null
  loading: boolean
}>()

const emit = defineEmits(['save'])
const dialog = defineModel<boolean>()
const formRef = ref<any>(null)

const formData = reactive({
  doc_name: '',
  notes: '', // Примечание тоже можно редактировать, если нужно
})

watch(
  () => props.item,
  (newItem) => {
    if (newItem) {
      formData.doc_name = newItem.doc_name
      // formData.notes = newItem.note; // Если в AssignedNumber будет note
    }
  },
)

async function save() {
  if (!props.item) return
  const { valid } = await formRef.value.validate()
  if (valid) {
    emit('save', { id: props.item.doc_no, payload: formData })
  }
}

function close() {
  dialog.value = false
}

const itemData = computed(() => props.item)
</script>
