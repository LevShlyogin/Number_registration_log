<template>
  <v-dialog v-model="dialog" persistent max-width="600px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Создание нового объекта оборудования</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="formRef">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.eq_type"
                  label="Тип оборудования*"
                  :rules="[rules.required]"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.factory_no" label="Заводской номер"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.station_no"
                  label="Станционный номер"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.station_object"
                  label="Станция / Объект"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="formData.notes" label="Примечание" rows="2"></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
        <small>*обязательное поле</small>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="close"> Отмена </v-btn>
        <v-btn color="blue-darken-1" variant="flat" @click="save" :loading="isSaving">
          Сохранить
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { EquipmentIn, EquipmentOut } from '@/types/api'

// Определяем пропсы и события
const dialog = defineModel<boolean>() // Упрощенный v-model для Vue 3.3+
const emit = defineEmits(['success'])

const formRef = ref<any>(null) // Ссылка на v-form
const formData = reactive<EquipmentIn>({
  factory_no: null,
  label: null,
  notes: null,
  order_no: null,
  station_no: null,
  station_object: null,
  eq_type: 'Турбина',
})
const rules = {
  required: (value: string) => !!value || 'Это поле обязательно.',
}

// Мутация для создания оборудования
const { mutate: createEquipment, isPending: isSaving } = useMutation({
  mutationFn: (newData: EquipmentIn) => apiClient.post<EquipmentOut>('/equipment', newData),
  onSuccess: (response) => {
    // При успехе отправляем событие 'success' с данными нового элемента
    emit('success', response.data)
    close() // Закрываем диалог
  },
  onError: (error) => {
    // TODO: Показать ошибку пользователю
    console.error('Failed to create equipment:', error)
  },
})

async function save() {
  const { valid } = await formRef.value.validate()
  if (valid) {
    createEquipment(formData)
  }
}

function close() {
  // Сбрасываем форму, если нужно
  formRef.value.reset()
  dialog.value = false
}
</script>
