<template>
  <v-btn icon @click="toggleTheme">
    <v-icon
      :icon="theme.global.current.value.dark ? 'mdi-white-balance-sunny' : 'mdi-weather-night'"
    ></v-icon>
    <v-tooltip activator="parent" location="bottom"> Переключить тему </v-tooltip>
  </v-btn>
</template>

<script setup lang="ts">
import { useTheme } from 'vuetify'

const theme = useTheme()

function toggleTheme() {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}
</script>
