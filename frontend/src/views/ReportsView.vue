<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h4 font-weight-bold mb-4">Отчеты</h1>
      </v-col>
    </v-row>

    <v-card flat class="border mb-6">
      <v-card-title>Фильтры</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="4">
            <v-text-field label="Станция / Объект" clearable></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-text-field label="Заводской номер" clearable></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-text-field label="Дата (с)" type="date"></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" variant="flat">Сформировать</v-btn>
        <v-btn>Сбросить</v-btn>
      </v-card-actions>
    </v-card>

    <v-card flat class="border">
      <v-card-title>Результаты</v-card-title>
      <v-data-table
        :headers="headers"
        :items="desserts"
        item-value="name"
        class="elevation-0"
      ></v-data-table>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
// Заглушки для таблицы
const headers = [
  { title: 'Станция', key: 'station' },
  { title: 'Зав. №', key: 'factory_no' },
  { title: 'Документ', key: 'doc_name' },
  { title: 'Номер', key: 'doc_no' },
  { title: 'Дата', key: 'date' },
]
const desserts = [
  { station: 'ТЭЦ-23', factory_no: '12345', doc_name: 'Чертеж', doc_no: 1001, date: '2024-01-01' },
]
</script>
