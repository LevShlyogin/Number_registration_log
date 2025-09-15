import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useWizardStore } from '@/stores/wizard.ts'

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
              props: true,
              // Навигационный хук (guard)
              beforeEnter: (to, from) => {
                const wizardStore = useWizardStore()
                // Разрешаем вход, только если оборудование выбрано ИЛИ
                // если мы пришли не из визарда (прямая ссылка)
                if (wizardStore.hasSelectedEquipment || from.name !== 'wizard-equipment') {
                  // При прямой загрузке, устанавливаем ID из URL в стор
                  if (!wizardStore.hasSelectedEquipment) {
                    wizardStore.setEquipment(Number(to.params.equipmentId))
                  }
                  return true
                }
                // Иначе возвращаем на первый шаг
                return { name: 'wizard-equipment' }
              },
            },
            {
              path: 'assign/:sessionId',
              name: 'wizard-assign',
              component: () => import('@/views/wizard/Step3Assign.vue'),
              props: true,
              beforeEnter: (to, from) => {
                const wizardStore = useWizardStore()
                if (wizardStore.hasActiveSession || from.name !== 'wizard-reserve') {
                  if (!wizardStore.hasActiveSession) {
                    // Здесь сложнее восстановить, т.к. нет номеров.
                    // Пока просто разрешаем, но в будущем можно делать API-запрос на восстановление сессии.
                  }
                  return true
                }
                return {
                  name: 'wizard-reserve',
                  params: { equipmentId: wizardStore.selectedEquipmentId },
                }
              },
            },
          ],
        },
      ],
    },
  ],
})

// Глобальный хук для сброса состояния визарда, если ушли с него
router.beforeEach((to, from) => {
  if (!to.path.startsWith('/wizard') && from.path.startsWith('/wizard')) {
    const wizardStore = useWizardStore()
    wizardStore.reset()
    console.log('Wizard state has been reset.')
  }
})

export default router
