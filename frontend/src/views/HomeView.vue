<template>
  <v-container>
    <v-row justify="center" align="center" style="min-height: 70vh">
      <v-col cols="12" md="8" class="text-center">
        <!-- Анимация появления -->
        <v-fade-transition appear>
          <div>
            <v-avatar size="80" class="mb-4 elevation-3">
              <v-img src="/logo.png"></v-img>
            </v-avatar>
            <h1 class="text-h3 font-weight-bold mb-3 text-primary">Журнал регистрации УТЗ</h1>
            <p class="text-h6 font-weight-light text-medium-emphasis mb-8">
              Система для регистрации номеров конструкторской документации.
            </p>
            <div class="d-flex justify-center flex-wrap ga-4">
              <v-btn
                color="primary"
                size="x-large"
                to="/wizard"
                variant="flat"
                class="elevation-2"
                prepend-icon="mdi-file-document-edit-outline"
              >
                Начать регистрацию
              </v-btn>
              <v-btn size="x-large" to="/reports" variant="outlined"> Перейти к отчетам </v-btn>
            </div>
          </div>
        </v-fade-transition>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts"></script>
