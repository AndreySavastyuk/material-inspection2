<template>
  <div class="home-view">
    <h1>Система контроля металла</h1>

    <div class="stats-grid">
      <Card v-for="stat in statistics" :key="stat.label">
        <template #header>
          <div class="stat-header">
            <i :class="stat.icon"></i>
            <span>{{ stat.label }}</span>
          </div>
        </template>
        <template #content>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-desc">{{ stat.description }}</div>
        </template>
      </Card>
    </div>

    <div class="recent-materials">
      <h2>Последние поступления</h2>
      <DataTable :value="recentMaterials" :loading="loading">
        <Column field="material_code" header="Код"></Column>
        <Column field="name" header="Наименование"></Column>
        <Column field="supplier" header="Поставщик"></Column>
        <Column field="status" header="Статус">
          <template #body="slotProps">
            <Tag :severity="getStatusSeverity(slotProps.data.status)">
              {{ getStatusLabel(slotProps.data.status) }}
            </Tag>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMaterialStore } from '@/stores/material'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const materialStore = useMaterialStore()

const statistics = ref([
  { label: 'Всего материалов', value: 0, icon: 'pi pi-box', description: 'На складе' },
  { label: 'На тестировании', value: 0, icon: 'pi pi-spin pi-spinner', description: 'В процессе' },
  { label: 'Одобрено', value: 0, icon: 'pi pi-check-circle', description: 'За месяц' },
  { label: 'Отклонено', value: 0, icon: 'pi pi-times-circle', description: 'За месяц' }
])

const recentMaterials = ref([])
const loading = ref(false)

const getStatusSeverity = (status) => {
  const severityMap = {
    'received': 'info',
    'quarantine': 'warn',
    'testing': 'secondary',
    'approved': 'success',
    'rejected': 'danger',
    'released': 'success'
  }
  return severityMap[status] || 'info'
}

const getStatusLabel = (status) => {
  const labelMap = {
    'received': 'Принят',
    'quarantine': 'Карантин',
    'testing': 'Тестирование',
    'approved': 'Одобрен',
    'rejected': 'Отклонен',
    'released': 'Выдан'
  }
  return labelMap[status] || status
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await materialStore.fetchMaterials({ limit: 5 })
    recentMaterials.value = data?.items || []

    // Обновляем статистику
    if (data?.items) {
      statistics.value[0].value = data.total || 0
      statistics.value[1].value = data.items.filter(m => m.status === 'testing').length
      statistics.value[2].value = data.items.filter(m => m.status === 'approved').length
      statistics.value[3].value = data.items.filter(m => m.status === 'rejected').length
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home-view {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  font-size: 16px;
  font-weight: 600;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 5px;
}

.recent-materials {
  margin-top: 40px;
}

.recent-materials h2 {
  margin-bottom: 20px;
}
</style>