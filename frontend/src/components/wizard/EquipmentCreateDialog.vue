<template>
  <v-dialog v-model="dialog" persistent max-width="700px">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Создание нового объекта оборудования</span>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" variant="text" @click="close"></v-btn>
      </v-card-title>
      <v-divider></v-divider>

      <v-form ref="formRef" v-model="isFormValid" lazy-validation>
        <v-card-text style="max-height: 70vh; overflow-y: auto">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="formData.eq_type"
                  :items="['Турбина', 'Вспомогательное оборудование']"
                  label="Тип оборудования*"
                  :rules="[rules.required]"
                  required
                  variant="outlined"
                  density="compact"
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.station_object"
                  label="Станция / Объект"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.station_no"
                  label="№ станционный"
                  :rules="[rules.stationNo]"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.factory_no"
                  label="№ заводской"
                  :rules="[rules.factoryNo]"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.order_no"
                  label="№ заказа"
                  placeholder="XXXXX-XX-XXXXX"
                  :rules="[rules.orderNo]"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.label"
                  label="Маркировка"
                  variant="outlined"
                  density="compact"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.notes"
                  label="Примечание"
                  rows="2"
                  variant="outlined"
                  density="compact"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-container>
          <small class="pl-4">* обязательное поле</small>
        </v-card-text>
      </v-form>

      <v-divider></v-divider>
      <v-card-actions class="pa-4">
        <v-spacer></v-spacer>
        <v-btn variant="text" @click="close">Отмена</v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="save"
          :loading="isSaving"
          :disabled="!isFormValid"
        >
          Сохранить и выбрать
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useMutation } from '@tanstack/vue-query'
import apiClient from '@/api'
import type { EquipmentIn, EquipmentOut } from '@/types/api'
import { useNotifier } from '@/composables/useNotifier'

const dialog = defineModel<boolean>()
const emit = defineEmits(['success'])

const formRef = ref<any>(null)
const isFormValid = ref(false)
const notifier = useNotifier()
const formData = reactive<Partial<EquipmentIn>>({
  eq_type: 'Турбина',
})

const rules = {
  required: (v: any) => !!v || 'Это поле обязательно.',
  factoryNo: (v: string) => !v || /^\d{1,5}$/.test(v) || 'Не более 5 цифр',
  stationNo: (v: string) => !v || /^\d{1,2}$/.test(v) || 'Не более 2 цифр',
  orderNo: (v: string) => !v || /^\d{5}-\d{2}-\d{5}$/.test(v) || 'Формат XXXXX-XX-XXXXX',
}

watch(
  () => formData.order_no,
  (newValue) => {
    if (newValue === null || newValue === undefined) return
    const digitsOnly = newValue.toString().replace(/\D/g, '')

    let formatted = ''
    if (digitsOnly.length > 0) {
      formatted = digitsOnly.substring(0, 5)
    }
    if (digitsOnly.length > 5) {
      formatted += '-' + digitsOnly.substring(5, 7)
    }
    if (digitsOnly.length > 7) {
      formatted += '-' + digitsOnly.substring(7, 12)
    }
    if (formatted !== newValue) {
      formData.order_no = formatted
    }
  },
)

watch(dialog, (newValue) => {
  if (newValue) {
    formRef.value?.reset()
    formRef.value?.resetValidation()
    Object.assign(formData, {
      eq_type: 'Турбина',
      station_object: '',
      station_no: '',
      factory_no: '',
      order_no: '',
      label: '',
      notes: '',
    })
  }
})

const { mutate: createEquipment, isPending: isSaving } = useMutation({
  mutationFn: (newData: EquipmentIn) => apiClient.post<EquipmentOut>('/equipment', newData),
  onSuccess: (response) => {
    notifier.success(`Объект "${response.data.eq_type}" успешно создан!`)
    emit('success', response.data)
  },
  onError: (error: any) => {
    const message = error.response?.data?.detail || error.message || 'Произошла неизвестная ошибка'
    notifier.error(`Ошибка создания: ${message}`)
  },
})

async function save() {
  const { valid } = await formRef.value.validate()
  if (valid) {
    createEquipment(formData as EquipmentIn)
  } else {
    notifier.warning('Пожалуйста, исправьте ошибки в форме.')
  }
}

function close() {
  dialog.value = false
}
</script>
