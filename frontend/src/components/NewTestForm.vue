<template>
  <div>
    <p>Форма создания испытания (в разработке)</p>
    <Button label="Отмена" @click="$emit('cancel')" />
  </div>
</template>

<script setup>
import Button from 'primevue/button'
defineEmits(['saved', 'cancel'])
</script>