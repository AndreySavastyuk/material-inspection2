<template>
  <div class="materials-view">
    <!-- Заголовок и действия -->
    <div class="page-header">
      <div class="header-content">
        <h1><i class="pi pi-box mr-2"></i>Материалы</h1>
        <p class="text-secondary">Управление материалами и входной контроль</p>
      </div>
      <div class="header-actions">
        <Button
          label="Экспорт"
          icon="pi pi-download"
          severity="secondary"
          outlined
          @click="exportMaterials"
          class="mr-2"
        />
        <Button
          label="Импорт"
          icon="pi pi-upload"
          severity="secondary"
          outlined
          @click="showImportDialog = true"
          class="mr-2"
        />
        <Button
          label="Новый материал"
          icon="pi pi-plus"
          severity="success"
          @click="showReceivingForm = true"
        />
      </div>
    </div>

    <!-- Статистика -->
    <div class="statistics-cards">
      <div class="stat-card">
        <div class="stat-icon bg-blue-100">
          <i class="pi pi-inbox text-blue-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Всего материалов</span>
          <span class="stat-value">{{ statistics.total }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-orange-100">
          <i class="pi pi-clock text-orange-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">В карантине</span>
          <span class="stat-value">{{ statistics.quarantine }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-purple-100">
          <i class="pi pi-search text-purple-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">На испытаниях</span>
          <span class="stat-value">{{ statistics.testing }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-green-100">
          <i class="pi pi-check-circle text-green-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Одобрено</span>
          <span class="stat-value">{{ statistics.approved }}</span>
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <Card class="mb-4">
      <template #content>
        <div class="filters-section">
          <div class="grid">
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <InputText
                  id="search"
                  v-model="filters.search"
                  @input="onFilterChange"
                  class="w-full"
                />
                <label for="search">Поиск</label>
              </span>
            </div>
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <MultiSelect
                  id="status"
                  v-model="filters.status"
                  :options="statusOptions"
                  optionLabel="label"
                  optionValue="value"
                  @change="onFilterChange"
                  class="w-full"
                  display="chip"
                />
                <label for="status">Статус</label>
              </span>
            </div>
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <MultiSelect
                  id="type"
                  v-model="filters.type"
                  :options="typeOptions"
                  optionLabel="label"
                  optionValue="value"
                  @change="onFilterChange"
                  class="w-full"
                  display="chip"
                />
                <label for="type">Тип материала</label>
              </span>
            </div>
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <Calendar
                  id="dateRange"
                  v-model="filters.dateRange"
                  selectionMode="range"
                  dateFormat="dd.mm.yy"
                  @date-select="onFilterChange"
                  class="w-full"
                  showIcon
                />
                <label for="dateRange">Период поступления</label>
              </span>
            </div>
          </div>
          <div class="filter-actions">
            <Button
              label="Сбросить"
              icon="pi pi-times"
              severity="secondary"
              text
              @click="resetFilters"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Таблица материалов -->
    <Card>
      <template #content>
        <DataTable
          :value="materials"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
          :loading="loading"
          :globalFilterFields="['material_code', 'name', 'supplier', 'grade']"
          responsiveLayout="scroll"
          stripedRows
          showGridlines
          :rowHover="true"
          @row-click="onRowClick"
          class="materials-table"
        >
          <!-- Колонка выбора -->
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>

          <!-- Код материала -->
          <Column field="material_code" header="Код" sortable style="min-width: 140px">
            <template #body="slotProps">
              <div class="code-cell">
                <span class="font-semibold">{{ slotProps.data.material_code }}</span>
                <Button
                  icon="pi pi-qrcode"
                  size="small"
                  text
                  rounded
                  @click.stop="showQRCode(slotProps.data)"
                  v-tooltip="'QR-код'"
                />
              </div>
            </template>
          </Column>

          <!-- Тип -->
          <Column field="material_type" header="Тип" sortable style="min-width: 120px">
            <template #body="slotProps">
              <Tag :value="getTypeLabel(slotProps.data.material_type)" :severity="getTypeSeverity(slotProps.data.material_type)" />
            </template>
          </Column>

          <!-- Наименование -->
          <Column field="name" header="Наименование" sortable style="min-width: 250px">
            <template #body="slotProps">
              <div>
                <div class="font-medium">{{ slotProps.data.name }}</div>
                <small class="text-secondary">
                  {{ slotProps.data.grade || '' }}
                  {{ slotProps.data.dimensions ? '• ' + slotProps.data.dimensions : '' }}
                </small>
              </div>
            </template>
          </Column>

          <!-- Поставщик -->
          <Column field="supplier" header="Поставщик" sortable style="min-width: 200px">
            <template #body="slotProps">
              <div class="supplier-cell">
                <span>{{ slotProps.data.supplier }}</span>
                <i
                  v-if="slotProps.data.metadata?.trusted_supplier"
                  class="pi pi-verified text-green-500 ml-2"
                  v-tooltip="'Проверенный поставщик'"
                ></i>
              </div>
            </template>
          </Column>

          <!-- Количество -->
          <Column field="quantity" header="Количество" sortable style="min-width: 120px">
            <template #body="slotProps">
              <span>{{ slotProps.data.quantity }} {{ slotProps.data.unit }}</span>
            </template>
          </Column>

          <!-- Статус -->
          <Column field="status" header="Статус" sortable style="min-width: 140px">
            <template #body="slotProps">
              <Tag
                :value="getStatusLabel(slotProps.data.status)"
                :severity="getStatusSeverity(slotProps.data.status)"
                :icon="getStatusIcon(slotProps.data.status)"
              />
            </template>
          </Column>

          <!-- Дата поступления -->
          <Column field="received_date" header="Дата поступления" sortable style="min-width: 140px">
            <template #body="slotProps">
              <span>{{ formatDate(slotProps.data.received_date) }}</span>
            </template>
          </Column>

          <!-- Место хранения -->
          <Column field="current_location" header="Место" style="min-width: 180px">
            <template #body="slotProps">
              <div class="location-cell">
                <i class="pi pi-map-marker text-secondary mr-1"></i>
                <span>{{ slotProps.data.current_location || 'Не указано' }}</span>
              </div>
            </template>
          </Column>

          <!-- Действия -->
          <Column header="Действия" style="min-width: 120px">
            <template #body="slotProps">
              <div class="actions-cell">
                <Button
                  icon="pi pi-eye"
                  size="small"
                  text
                  rounded
                  @click.stop="viewMaterial(slotProps.data)"
                  v-tooltip="'Просмотр'"
                />
                <Button
                  icon="pi pi-pencil"
                  size="small"
                  text
                  rounded
                  @click.stop="editMaterial(slotProps.data)"
                  v-tooltip="'Редактировать'"
                />
                <Button
                  icon="pi pi-ellipsis-v"
                  size="small"
                  text
                  rounded
                  @click.stop="toggleMenu($event, slotProps.data)"
                  v-tooltip="'Дополнительно'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Контекстное меню -->
    <Menu ref="menu" :model="menuItems" :popup="true" />

    <!-- Диалог просмотра материала -->
    <Dialog
      v-model:visible="showDetailDialog"
      :header="`Материал: ${selectedMaterial?.material_code}`"
      :modal="true"
      :style="{ width: '800px' }"
      :maximizable="true"
    >
      <MaterialDetail v-if="selectedMaterial" :material="selectedMaterial" />
    </Dialog>

    <!-- Диалог QR-кода -->
    <Dialog
      v-model:visible="showQRDialog"
      header="QR-код материала"
      :modal="true"
      :style="{ width: '400px' }"
    >
      <div class="qr-dialog-content">
        <div class="qr-code-container">
          <canvas ref="qrCanvas"></canvas>
        </div>
        <div class="qr-info">
          <p><strong>Код:</strong> {{ selectedMaterial?.material_code }}</p>
          <p><strong>Наименование:</strong> {{ selectedMaterial?.name }}</p>
        </div>
      </div>
      <template #footer>
        <Button label="Скачать" icon="pi pi-download" @click="downloadQR" />
        <Button label="Печать" icon="pi pi-print" @click="printQR" />
      </template>
    </Dialog>

    <!-- Форма приемки материала -->
    <Dialog
      v-model:visible="showReceivingForm"
      header="Приемка нового материала"
      :modal="true"
      :style="{ width: '90vw', maxWidth: '1200px' }"
      :maximizable="true"
      :closable="false"
    >
      <MaterialReceivingForm @close="showReceivingForm = false" @saved="onMaterialSaved" />
    </Dialog>

    <!-- Диалог импорта -->
    <Dialog
      v-model:visible="showImportDialog"
      header="Импорт материалов"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="import-dialog">
        <FileUpload
          mode="basic"
          accept=".xlsx,.xls,.csv"
          :maxFileSize="10000000"
          @select="onFileSelect"
          chooseLabel="Выбрать файл"
        />
        <div class="mt-3">
          <Button
            label="Скачать шаблон"
            icon="pi pi-download"
            severity="secondary"
            outlined
            @click="downloadTemplate"
            class="w-full"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Отмена" severity="secondary" @click="showImportDialog = false" />
        <Button label="Импортировать" icon="pi pi-upload" @click="importFile" :disabled="!selectedFile" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { materialService } from '@/services/materialService'
import MaterialReceivingForm from '@/components/MaterialReceivingForm.vue'
import MaterialDetail from '@/components/MaterialDetail.vue'
import QRCode from 'qrcode'

const toast = useToast()
const router = useRouter()

// Состояние
const loading = ref(false)
const materials = ref([])
const selectedMaterial = ref(null)
const showDetailDialog = ref(false)
const showQRDialog = ref(false)
const showReceivingForm = ref(false)
const showImportDialog = ref(false)
const selectedFile = ref(null)
const menu = ref()
const qrCanvas = ref()

// Статистика
const statistics = reactive({
  total: 0,
  quarantine: 0,
  testing: 0,
  approved: 0
})

// Фильтры
const filters = reactive({
  search: '',
  status: [],
  type: [],
  dateRange: null
})

// Опции для фильтров
const statusOptions = ref([
  { label: 'Получен', value: 'received' },
  { label: 'Карантин', value: 'quarantine' },
  { label: 'На испытаниях', value: 'testing' },
  { label: 'Одобрен', value: 'approved' },
  { label: 'Выдан', value: 'released' },
  { label: 'Отклонен', value: 'rejected' }
])

const typeOptions = ref([
  { label: 'Листовой прокат', value: 'sheet' },
  { label: 'Сортовой прокат', value: 'profile' },
  { label: 'Трубы', value: 'pipe' },
  { label: 'Проволока', value: 'wire' },
  { label: 'Арматура', value: 'rebar' },
  { label: 'Прочее', value: 'other' }
])

// Пункты контекстного меню
const menuItems = ref([
  {
    label: 'Изменить статус',
    icon: 'pi pi-sync',
    items: [
      { label: 'Отправить в карантин', command: () => changeStatus('quarantine') },
      { label: 'Начать испытания', command: () => changeStatus('testing') },
      { label: 'Одобрить', command: () => changeStatus('approved') },
      { label: 'Выдать в производство', command: () => changeStatus('released') }
    ]
  },
  { separator: true },
  {
    label: 'Документы',
    icon: 'pi pi-file',
    command: () => viewDocuments()
  },
  {
    label: 'История',
    icon: 'pi pi-history',
    command: () => viewHistory()
  },
  {
    label: 'Дублировать',
    icon: 'pi pi-copy',
    command: () => duplicateMaterial()
  },
  { separator: true },
  {
    label: 'Удалить',
    icon: 'pi pi-trash',
    command: () => deleteMaterial()
  }
])

// Методы
const loadMaterials = async () => {
  try {
    loading.value = true
    const response = await materialService.getAll(filters)
    materials.value = response.items || []

    // Обновляем статистику
    updateStatistics()
  } catch (error) {
    console.error('Ошибка загрузки материалов:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить список материалов',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const updateStatistics = () => {
  statistics.total = materials.value.length
  statistics.quarantine = materials.value.filter(m => m.status === 'quarantine').length
  statistics.testing = materials.value.filter(m => m.status === 'testing').length
  statistics.approved = materials.value.filter(m => m.status === 'approved').length
}

const onFilterChange = () => {
  loadMaterials()
}

const resetFilters = () => {
  filters.search = ''
  filters.status = []
  filters.type = []
  filters.dateRange = null
  loadMaterials()
}

const onRowClick = (event) => {
  viewMaterial(event.data)
}

const viewMaterial = (material) => {
  selectedMaterial.value = material
  showDetailDialog.value = true
}

const editMaterial = (material) => {
  router.push(`/materials/edit/${material.id}`)
}

const toggleMenu = (event, material) => {
  selectedMaterial.value = material
  menu.value.toggle(event)
}

const showQRCode = async (material) => {
  selectedMaterial.value = material
  showQRDialog.value = true

  // Генерируем QR-код
  setTimeout(async () => {
    if (qrCanvas.value) {
      await QRCode.toCanvas(qrCanvas.value, material.material_code, {
        width: 300,
        margin: 2
      })
    }
  }, 100)
}

const downloadQR = () => {
  const link = document.createElement('a')
  link.download = `${selectedMaterial.value.material_code}.png`
  link.href = qrCanvas.value.toDataURL()
  link.click()
}

const printQR = () => {
  const printWindow = window.open('', '_blank')
  printWindow.document.write(`
    <html>
      <head><title>QR Code - ${selectedMaterial.value.material_code}</title></head>
      <body style="text-align: center; padding: 20px;">
        <h2>${selectedMaterial.value.material_code}</h2>
        <img src="${qrCanvas.value.toDataURL()}" />
        <p>${selectedMaterial.value.name}</p>
      </body>
    </html>
  `)
  printWindow.document.close()
  printWindow.print()
}

const changeStatus = async (newStatus) => {
  try {
    await materialService.changeStatus(selectedMaterial.value.id, newStatus)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Статус материала изменен',
      life: 3000
    })
    loadMaterials()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось изменить статус',
      life: 5000
    })
  }
}

const viewDocuments = () => {
  router.push(`/materials/${selectedMaterial.value.id}/documents`)
}

const viewHistory = () => {
  router.push(`/materials/${selectedMaterial.value.id}/history`)
}

const duplicateMaterial = async () => {
  try {
    await materialService.duplicate(selectedMaterial.value.id)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Материал дублирован',
      life: 3000
    })
    loadMaterials()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось дублировать материал',
      life: 5000
    })
  }
}

const deleteMaterial = async () => {
  // Здесь должен быть диалог подтверждения
  try {
    await materialService.delete(selectedMaterial.value.id)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Материал удален',
      life: 3000
    })
    loadMaterials()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось удалить материал',
      life: 5000
    })
  }
}

const exportMaterials = async () => {
  try {
    await materialService.exportToExcel(filters)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Данные экспортированы',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось экспортировать данные',
      life: 5000
    })
  }
}

const onFileSelect = (event) => {
  selectedFile.value = event.files[0]
}

const downloadTemplate = async () => {
  try {
    await materialService.getImportTemplate()
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Шаблон загружен',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить шаблон',
      life: 5000
    })
  }
}

const importFile = async () => {
  if (!selectedFile.value) return

  try {
    await materialService.importFromExcel(selectedFile.value)
    showImportDialog.value = false
    selectedFile.value = null
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Данные импортированы',
      life: 3000
    })
    loadMaterials()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось импортировать данные',
      life: 5000
    })
  }
}

const onMaterialSaved = () => {
  showReceivingForm.value = false
  loadMaterials()
}

// Вспомогательные функции
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

const getStatusLabel = (status) => {
  const labels = {
    'received': 'Получен',
    'quarantine': 'Карантин',
    'testing': 'Испытания',
    'approved': 'Одобрен',
    'released': 'Выдан',
    'rejected': 'Отклонен'
  }
  return labels[status] || status
}

const getStatusSeverity = (status) => {
  const severities = {
    'received': 'info',
    'quarantine': 'warning',
    'testing': 'secondary',
    'approved': 'success',
    'released': 'primary',
    'rejected': 'danger'
  }
  return severities[status] || 'secondary'
}

const getStatusIcon = (status) => {
  const icons = {
    'received': 'pi pi-inbox',
    'quarantine': 'pi pi-clock',
    'testing': 'pi pi-search',
    'approved': 'pi pi-check-circle',
    'released': 'pi pi-send',
    'rejected': 'pi pi-times-circle'
  }
  return icons[status]
}

const getTypeLabel = (type) => {
  const labels = {
    'sheet': 'Лист',
    'profile': 'Профиль',
    'pipe': 'Труба',
    'wire': 'Проволока',
    'rebar': 'Арматура',
    'other': 'Прочее'
  }
  return labels[type] || type
}

const getTypeSeverity = (type) => {
  const severities = {
    'sheet': 'primary',
    'profile': 'success',
    'pipe': 'info',
    'wire': 'warning',
    'rebar': 'danger',
    'other': 'secondary'
  }
  return severities[type] || 'secondary'
}

// Хук жизненного цикла
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.materials-view {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header-content h1 {
  margin: 0;
  font-size: 2rem;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

/* Карточки статистики */
.statistics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid var(--surface-border);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

/* Фильтры */
.filters-section {
  position: relative;
}

.filter-actions {
  position: absolute;
  top: 0;
  right: 0;
}

/* Таблица */
.materials-table .code-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.materials-table .supplier-cell {
  display: flex;
  align-items: center;
}

.materials-table .location-cell {
  display: flex;
  align-items: center;
}

.materials-table .actions-cell {
  display: flex;
  gap: 0.25rem;
}

/* QR диалог */
.qr-dialog-content {
  text-align: center;
}

.qr-code-container {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
}

.qr-info p {
  margin: 0.5rem 0;
}

/* Импорт диалог */
.import-dialog {
  padding: 1rem 0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .statistics-cards {
    grid-template-columns: 1fr;
  }
}
</style>