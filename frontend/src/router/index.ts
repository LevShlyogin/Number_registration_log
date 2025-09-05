import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout, // Все роуты будут использовать этот layout
      children: [
        {
          path: '', // Главная страница
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
        },
        // --- Группа роутов для Wizard-а ---
        {
          path: 'wizard',
          name: 'wizard',
          // Можно создать компонент-обертку для визарда с индикатором шагов
          component: () => import('@/views/wizard/WizardWrapper.vue'),
          redirect: '/wizard/equipment', // При переходе на /wizard, сразу редирект на первый шаг
          children: [
            {
              path: 'equipment',
              name: 'wizard-equipment',
              component: () => import('@/views/wizard/Step1Equipment.vue'),
            },
            {
              path: 'reserve/:equipmentId',
              name: 'wizard-reserve',
              component: () => import('@/views/wizard/Step2Reserve.vue'),
              props: true, // Передавать :equipmentId как пропс в компонент
            },
            {
              path: 'assign/:sessionId',
              name: 'wizard-assign',
              component: () => import('@/views/wizard/Step3Assign.vue'),
              props: true, // Передавать :sessionId как пропс в компонент
            },
          ],
        },
        // --- Отдельная страница для Отчетов ---
        {
          path: 'reports',
          name: 'reports',
          component: () => import('@/views/ReportsView.vue'),
        },
        // --- Отдельная страница для Админки ---
        {
          path: 'admin',
          name: 'admin',
          component: () => import('@/views/AdminView.vue'),
        },
      ],
    },
  ],
})

export default router
