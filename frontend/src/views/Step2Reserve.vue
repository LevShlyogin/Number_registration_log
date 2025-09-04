<script setup lang="ts">
async function onNumbersReserved(response: { session_id: string; reserved_numbers: number[] }) {
  wizardStore.setSession(response.session_id, response.reserved_numbers)
  router.push({ name: 'wizard-assign', params: { sessionId: response.session_id } })
}
</script>
