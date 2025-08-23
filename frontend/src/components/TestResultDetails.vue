<template>
  <div>
    <p>Детали испытания #{{ test?.id || 'N/A' }}</p>
    <pre>{{ JSON.stringify(test, null, 2) }}</pre>
  </div>
</template>

<script setup>
defineProps({
  test: Object
})
</script>