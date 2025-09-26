<template>
  <v-card flat class="border mb-6">
    <v-card-title class="d-flex align-center">
      <v-icon start icon="mdi-filter-variant"></v-icon>
      Фильтры
      <v-spacer></v-spacer>
      <v-btn size="small" variant="text" prepend-icon="mdi-close" @click="reset"> Сбросить </v-btn>
    </v-card-title>
    <v-divider></v-divider>
    <v-card-text>
      <!-- Используем v-model:model-value для двусторонней привязки -->
      <v-row>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.station_object"
            label="Станция/Объект"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.station_no"
            label="№ станционный"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.factory_no"
            label="№ заводской"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.order_no"
            label="№ заказа"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.label"
            label="Маркировка"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.doc_name"
            label="Имя документа"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.username"
            label="Пользователь"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.eq_type"
            label="Тип оборудования"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.date_from"
            label="Дата от"
            type="date"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
        <v-col cols="12" sm="6" md="3"
          ><v-text-field
            v-model="modelValue.date_to"
            label="Дата до"
            type="date"
            clearable
            hide-details="auto"
          ></v-text-field
        ></v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { SearchParams } from '@/types/api'

const modelValue = defineModel<Partial<SearchParams>>({ required: true })

const emit = defineEmits(['reset'])

function reset() {
  emit('reset')
}
</script>
