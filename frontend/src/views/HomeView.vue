<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" class="text-center">
        <h1 class="text-h3 font-weight-bold mb-4">Журнал регистрации УТЗ</h1>
        <p class="text-h6 font-weight-light mb-8">
          Система для регистрации оборудования и резервирования номеров.
        </p>
        <v-btn color="primary" size="large" to="/wizard">
          <v-icon start icon="mdi-play-circle-outline"></v-icon>
          Начать работу
        </v-btn>
        <v-btn class="ml-4" size="large" to="/reports" variant="outlined">
          <v-icon start icon="mdi-chart-bar"></v-icon>
          Перейти к отчетам
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>