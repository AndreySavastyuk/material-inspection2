<template>
  <div>
    <p>Редактирование испытания (в разработке)</p>
    <Button label="Отмена" @click="$emit('cancel')" />
  </div>
</template>

<script setup>
import Button from 'primevue/button'
defineProps({
  test: Object
})
defineEmits(['saved', 'cancel'])
</script>