<template>
  <div class="materials-view">
    <div class="materials-header">
      <h1>Материалы</h1>
      <Button
        label="Добавить материал"
        icon="pi pi-plus"
        @click="showCreateDialog = true"
        v-if="canCreate"
      />
    </div>

    <div class="filters">
      <InputText
        v-model="searchQuery"
        placeholder="Поиск..."
        @input="onSearch"
      />
      <Dropdown
        v-model="selectedStatus"
        :options="statusOptions"
        optionLabel="label"
        optionValue="value"
        placeholder="Статус"
        @change="onFilterChange"
      />
    </div>

    <DataTable
      :value="materials"
      :loading="loading"
      paginator
      :rows="10"
      responsiveLayout="scroll"
    >
      <Column field="material_code" header="Код" sortable></Column>
      <Column field="name" header="Наименование" sortable></Column>
      <Column field="material_type" header="Тип"></Column>
      <Column field="supplier" header="Поставщик"></Column>
      <Column field="quantity" header="Количество">
        <template #body="slotProps">
          {{ slotProps.data.quantity }} {{ slotProps.data.unit }}
        </template>
      </Column>
      <Column field="status" header="Статус">
        <template #body="slotProps">
          <Tag :severity="getStatusSeverity(slotProps.data.status)">
            {{ getStatusLabel(slotProps.data.status) }}
          </Tag>
        </template>
      </Column>
      <Column header="Действия">
        <template #body="slotProps">
          <Button
            icon="pi pi-eye"
            class="p-button-text p-button-sm"
            @click="viewMaterial(slotProps.data)"
          />
          <Button
            icon="pi pi-pencil"
            class="p-button-text p-button-sm"
            @click="editMaterial(slotProps.data)"
            v-if="canEdit"
          />
        </template>
      </Column>
    </DataTable>

    <!-- Диалог создания материала -->
    <Dialog
      v-model:visible="showCreateDialog"
      header="Новый материал"
      :modal="true"
      :style="{width: '50vw'}"
    >
      <div class="form-grid">
        <div class="field">
          <label>Код материала</label>
          <InputText v-model="newMaterial.material_code" />
        </div>
        <div class="field">
          <label>Наименование</label>
          <InputText v-model="newMaterial.name" />
        </div>
        <div class="field">
          <label>Тип</label>
          <Dropdown
            v-model="newMaterial.material_type"
            :options="materialTypes"
            optionLabel="label"
            optionValue="value"
          />
        </div>
        <div class="field">
          <label>Поставщик</label>
          <InputText v-model="newMaterial.supplier" />
        </div>
        <div class="field">
          <label>Количество</label>
          <InputNumber v-model="newMaterial.quantity" />
        </div>
        <div class="field">
          <label>Единица измерения</label>
          <InputText v-model="newMaterial.unit" />
        </div>
      </div>
      <template #footer>
        <Button label="Отмена" @click="showCreateDialog = false" class="p-button-text" />
        <Button label="Сохранить" @click="createMaterial" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useMaterialStore } from '@/stores/material'
import { useToast } from 'primevue/usetoast'

import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import InputNumber from 'primevue/inputnumber'

const userStore = useUserStore()
const materialStore = useMaterialStore()
const toast = useToast()

const materials = computed(() => materialStore.materials)
const loading = computed(() => materialStore.loading)

const searchQuery = ref('')
const selectedStatus = ref(null)
const showCreateDialog = ref(false)

const newMaterial = ref({
  material_code: '',
  name: '',
  material_type: 'steel',
  supplier: '',
  quantity: 0,
  unit: 'kg'
})

const statusOptions = [
  { label: 'Все', value: null },
  { label: 'Принят', value: 'received' },
  { label: 'Карантин', value: 'quarantine' },
  { label: 'Тестирование', value: 'testing' },
  { label: 'Одобрен', value: 'approved' },
  { label: 'Отклонен', value: 'rejected' },
  { label: 'Выдан', value: 'released' }
]

const materialTypes = [
  { label: 'Сталь', value: 'steel' },
  { label: 'Алюминий', value: 'aluminum' },
  { label: 'Медь', value: 'copper' },
  { label: 'Латунь', value: 'brass' },
  { label: 'Нержавеющая сталь', value: 'stainless_steel' }
]

const canCreate = computed(() => {
  return userStore.currentRole === 'warehouse_keeper' ||
         userStore.currentRole === 'administrator'
})

const canEdit = computed(() => {
  return userStore.currentRole === 'administrator'
})

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

const onSearch = () => {
  loadMaterials()
}

const onFilterChange = () => {
  loadMaterials()
}

const loadMaterials = async () => {
  const filters = {
    search: searchQuery.value,
    status: selectedStatus.value
  }
  await materialStore.fetchMaterials(filters)
}

const createMaterial = async () => {
  try {
    await materialStore.createMaterial(newMaterial.value)
    showCreateDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Материал создан',
      life: 3000
    })
    // Reset form
    newMaterial.value = {
      material_code: '',
      name: '',
      material_type: 'steel',
      supplier: '',
      quantity: 0,
      unit: 'kg'
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось создать материал',
      life: 5000
    })
  }
}

const viewMaterial = (material) => {
  // Переход на страницу детального просмотра
  console.log('View material:', material)
}

const editMaterial = (material) => {
  // Открытие диалога редактирования
  console.log('Edit material:', material)
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.materials-view {
  padding: 20px;
}

.materials-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field label {
  font-weight: 500;
  color: var(--text-secondary);
}
</style>