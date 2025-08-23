<template>
  <div class="material-detail">
    <TabView>
      <!-- Основная информация -->
      <TabPanel header="Основная информация">
        <div class="info-section">
          <div class="info-grid">
            <div class="info-group">
              <label>Код материала:</label>
              <span class="value font-semibold">{{ material.material_code }}</span>
            </div>
            <div class="info-group">
              <label>Статус:</label>
              <Tag
                :value="getStatusLabel(material.status)"
                :severity="getStatusSeverity(material.status)"
              />
            </div>
            <div class="info-group">
              <label>Тип материала:</label>
              <span class="value">{{ getTypeLabel(material.material_type) }}</span>
            </div>
            <div class="info-group">
              <label>Наименование:</label>
              <span class="value">{{ material.name }}</span>
            </div>
            <div class="info-group">
              <label>Марка/Сплав:</label>
              <span class="value">{{ material.grade || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Стандарт:</label>
              <span class="value">{{ material.standard || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Размеры:</label>
              <span class="value">{{ material.dimensions || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Количество:</label>
              <span class="value">{{ material.quantity }} {{ material.unit }}</span>
            </div>
            <div class="info-group">
              <label>Общий вес:</label>
              <span class="value">{{ material.total_weight ? material.total_weight + ' кг' : '-' }}</span>
            </div>
            <div class="info-group">
              <label>Место хранения:</label>
              <span class="value">
                <i class="pi pi-map-marker mr-1"></i>
                {{ material.current_location || 'Не указано' }}
              </span>
            </div>
          </div>

          <Divider />

          <div class="info-grid">
            <div class="info-group">
              <label>Поставщик:</label>
              <span class="value">
                {{ material.supplier }}
                <i
                  v-if="material.metadata?.trusted_supplier"
                  class="pi pi-verified text-green-500 ml-2"
                  v-tooltip="'Проверенный поставщик'"
                ></i>
              </span>
            </div>
            <div class="info-group">
              <label>Сертификат поставщика:</label>
              <span class="value">{{ material.supplier_certificate_number || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Номер партии:</label>
              <span class="value">{{ material.batch_number || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Номер плавки:</label>
              <span class="value">{{ material.heat_number || '-' }}</span>
            </div>
            <div class="info-group">
              <label>Дата поступления:</label>
              <span class="value">{{ formatDate(material.received_date) }}</span>
            </div>
            <div class="info-group">
              <label>Номер накладной:</label>
              <span class="value">{{ material.metadata?.invoice_number || '-' }}</span>
            </div>
          </div>

          <div v-if="material.notes" class="notes-section">
            <label>Примечания:</label>
            <p class="notes-text">{{ material.notes }}</p>
          </div>
        </div>
      </TabPanel>

      <!-- Результаты испытаний -->
      <TabPanel header="Испытания">
        <div class="tests-section">
          <div class="tests-header">
            <h4>Результаты испытаний</h4>
            <Button
              label="Добавить результат"
              icon="pi pi-plus"
              size="small"
              @click="showAddTestDialog = true"
            />
          </div>

          <DataTable
            :value="testResults"
            :loading="loadingTests"
            responsiveLayout="scroll"
            stripedRows
          >
            <template #empty>
              <div class="text-center py-4">
                <i class="pi pi-inbox text-4xl text-gray-400 mb-3"></i>
                <p class="text-gray-500">Испытания не проводились</p>
              </div>
            </template>

            <Column field="test_type" header="Тип испытания">
              <template #body="slotProps">
                {{ getTestTypeLabel(slotProps.data.test_type) }}
              </template>
            </Column>
            <Column field="test_category" header="Категория">
              <template #body="slotProps">
                <Tag
                  :value="slotProps.data.test_category === 'destructive' ? 'Разрушающий' : 'Неразрушающий'"
                  :severity="slotProps.data.test_category === 'destructive' ? 'danger' : 'info'"
                />
              </template>
            </Column>
            <Column field="tested_at" header="Дата проведения">
              <template #body="slotProps">
                {{ formatDateTime(slotProps.data.tested_at) }}
              </template>
            </Column>
            <Column field="pass_fail" header="Результат">
              <template #body="slotProps">
                <Tag
                  :value="slotProps.data.pass_fail === 'PASS' ? 'Пройдено' : 'Не пройдено'"
                  :severity="slotProps.data.pass_fail === 'PASS' ? 'success' : 'danger'"
                  :icon="slotProps.data.pass_fail === 'PASS' ? 'pi pi-check' : 'pi pi-times'"
                />
              </template>
            </Column>
            <Column field="tested_by" header="Исполнитель">
              <template #body="slotProps">
                {{ getUserName(slotProps.data.tested_by) }}
              </template>
            </Column>
            <Column header="Действия">
              <template #body="slotProps">
                <Button
                  icon="pi pi-eye"
                  size="small"
                  text
                  rounded
                  @click="viewTestDetails(slotProps.data)"
                  v-tooltip="'Подробности'"
                />
                <Button
                  icon="pi pi-file-pdf"
                  size="small"
                  text
                  rounded
                  @click="downloadTestReport(slotProps.data)"
                  v-tooltip="'Скачать отчет'"
                />
              </template>
            </Column>
          </DataTable>

          <!-- График результатов испытаний -->
          <div v-if="testResults.length > 0" class="test-charts mt-4">
            <Card>
              <template #title>
                <i class="pi pi-chart-line mr-2"></i>
                Анализ результатов
              </template>
              <template #content>
                <div class="charts-grid">
                  <div class="chart-container">
                    <h5>Распределение по типам</h5>
                    <Chart type="doughnut" :data="testTypeChartData" :options="chartOptions" />
                  </div>
                  <div class="chart-container">
                    <h5>Результаты испытаний</h5>
                    <Chart type="bar" :data="testResultChartData" :options="barChartOptions" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>

      <!-- Документы -->
      <TabPanel header="Документы">
        <div class="documents-section">
          <div class="documents-header">
            <h4>Прикрепленные документы</h4>
            <Button
              label="Загрузить документ"
              icon="pi pi-upload"
              size="small"
              @click="showUploadDialog = true"
            />
          </div>

          <div class="documents-grid">
            <div v-for="doc in documents" :key="doc.id" class="document-card">
              <div class="document-icon">
                <i :class="getDocumentIcon(doc.type)" class="text-4xl"></i>
              </div>
              <div class="document-info">
                <h5>{{ doc.name }}</h5>
                <p class="text-sm text-gray-500">
                  {{ formatFileSize(doc.size) }} • {{ formatDate(doc.uploaded_at) }}
                </p>
              </div>
              <div class="document-actions">
                <Button
                  icon="pi pi-download"
                  size="small"
                  text
                  rounded
                  @click="downloadDocument(doc)"
                  v-tooltip="'Скачать'"
                />
                <Button
                  icon="pi pi-eye"
                  size="small"
                  text
                  rounded
                  @click="previewDocument(doc)"
                  v-tooltip="'Просмотр'"
                />
                <Button
                  icon="pi pi-trash"
                  size="small"
                  text
                  rounded
                  severity="danger"
                  @click="deleteDocument(doc)"
                  v-tooltip="'Удалить'"
                />
              </div>
            </div>
          </div>

          <div v-if="documents.length === 0" class="empty-state">
            <i class="pi pi-folder-open text-5xl text-gray-400"></i>
            <p class="mt-3 text-gray-500">Нет прикрепленных документов</p>
          </div>
        </div>
      </TabPanel>

      <!-- История изменений -->
      <TabPanel header="История">
        <div class="history-section">
          <Timeline :value="workflowHistory" align="alternate">
            <template #marker="slotProps">
              <span class="timeline-marker" :style="{ backgroundColor: getStatusColor(slotProps.item.state_name) }">
                <i :class="getStatusIcon(slotProps.item.state_name)"></i>
              </span>
            </template>
            <template #content="slotProps">
              <Card>
                <template #title>
                  {{ getStatusLabel(slotProps.item.state_name) }}
                </template>
                <template #subtitle>
                  {{ formatDateTime(slotProps.item.changed_at) }}
                </template>
                <template #content>
                  <p class="mb-2">{{ slotProps.item.reason }}</p>
                  <p v-if="slotProps.item.notes" class="text-sm text-gray-600">
                    <i class="pi pi-comment mr-1"></i>
                    {{ slotProps.item.notes }}
                  </p>
                  <p class="text-sm text-gray-500 mt-2">
                    <i class="pi pi-user mr-1"></i>
                    {{ getUserName(slotProps.item.changed_by) }}
                  </p>
                </template>
              </Card>
            </template>
          </Timeline>

          <div v-if="workflowHistory.length === 0" class="empty-state">
            <i class="pi pi-history text-5xl text-gray-400"></i>
            <p class="mt-3 text-gray-500">История изменений пуста</p>
          </div>
        </div>
      </TabPanel>

      <!-- Workflow -->
      <TabPanel header="Workflow">
        <div class="workflow-section">
          <div class="current-status">
            <h4>Текущий статус</h4>
            <div class="status-display">
              <Tag
                :value="getStatusLabel(material.status)"
                :severity="getStatusSeverity(material.status)"
                class="text-lg px-3 py-2"
              />
            </div>
          </div>

          <Divider />

          <div class="available-transitions">
            <h4>Доступные переходы</h4>
            <div class="transitions-grid">
              <div v-for="transition in availableTransitions" :key="transition.to" class="transition-card">
                <div class="transition-info">
                  <i :class="getStatusIcon(transition.to)" class="text-2xl mb-2"></i>
                  <h5>{{ getStatusLabel(transition.to) }}</h5>
                  <p class="text-sm text-gray-600">{{ transition.description }}</p>
                </div>
                <Button
                  :label="transition.action"
                  :severity="getStatusSeverity(transition.to)"
                  @click="executeTransition(transition)"
                  class="w-full mt-3"
                />
              </div>
            </div>

            <div v-if="availableTransitions.length === 0" class="empty-state">
              <i class="pi pi-info-circle text-4xl text-gray-400"></i>
              <p class="mt-3 text-gray-500">Нет доступных переходов из текущего статуса</p>
            </div>
          </div>

          <!-- Визуализация workflow -->
          <div class="workflow-diagram mt-4">
            <Card>
              <template #title>
                <i class="pi pi-sitemap mr-2"></i>
                Схема процесса
              </template>
              <template #content>
                <div class="workflow-visualization">
                  <div class="workflow-step" v-for="step in workflowSteps" :key="step.value"
                       :class="{ 'active': step.value === material.status, 'completed': isStepCompleted(step.value) }">
                    <div class="step-icon">
                      <i :class="step.icon"></i>
                    </div>
                    <div class="step-label">{{ step.label }}</div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>
    </TabView>

    <!-- Диалог добавления теста -->
    <Dialog
      v-model:visible="showAddTestDialog"
      header="Добавить результат испытания"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <AddTestResult
        :materialId="material.id"
        @saved="onTestAdded"
        @cancel="showAddTestDialog = false"
      />
    </Dialog>

    <!-- Диалог загрузки документа -->
    <Dialog
      v-model:visible="showUploadDialog"
      header="Загрузить документ"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <FileUpload
        mode="basic"
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
        :maxFileSize="10000000"
        @select="onFileUpload"
        chooseLabel="Выбрать файл"
        class="w-full"
      />
    </Dialog>

    <!-- Диалог деталей теста -->
    <Dialog
      v-model:visible="showTestDetailsDialog"
      :header="`Результаты: ${getTestTypeLabel(selectedTest?.test_type)}`"
      :modal="true"
      :style="{ width: '700px' }"
      :maximizable="true"
    >
      <TestResultDetails v-if="selectedTest" :test="selectedTest" />
    </Dialog>

    <!-- Диалог перехода workflow -->
    <Dialog
      v-model:visible="showTransitionDialog"
      :header="`Изменить статус на: ${getStatusLabel(selectedTransition?.to)}`"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="transition-form">
        <div class="field">
          <label for="transition_notes">Примечание</label>
          <Textarea
            id="transition_notes"
            v-model="transitionNotes"
            rows="4"
            class="w-full"
            placeholder="Укажите причину изменения статуса..."
          />
        </div>
      </div>
      <template #footer>
        <Button
          label="Отмена"
          severity="secondary"
          @click="showTransitionDialog = false"
        />
        <Button
          label="Подтвердить"
          :severity="getStatusSeverity(selectedTransition?.to)"
          @click="confirmTransition"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { materialService } from '@/services/materialService'
import { testService } from '@/services/testService'
import { documentService } from '@/services/documentService'
import { userService } from '@/services/userService'
import AddTestResult from './AddTestResult.vue'
import TestResultDetails from './TestResultDetails.vue'
import Chart from 'primevue/chart'

const props = defineProps({
  material: {
    type: Object,
    required: true
  }
})

const toast = useToast()

// Состояние
const loadingTests = ref(false)
const testResults = ref([])
const documents = ref([])
const workflowHistory = ref([])
const availableTransitions = ref([])
const users = ref({})

// Диалоги
const showAddTestDialog = ref(false)
const showUploadDialog = ref(false)
const showTestDetailsDialog = ref(false)
const showTransitionDialog = ref(false)

// Выбранные элементы
const selectedTest = ref(null)
const selectedTransition = ref(null)
const transitionNotes = ref('')

// Шаги workflow
const workflowSteps = [
  { value: 'received', label: 'Получен', icon: 'pi pi-inbox' },
  { value: 'quarantine', label: 'Карантин', icon: 'pi pi-clock' },
  { value: 'testing', label: 'Испытания', icon: 'pi pi-search' },
  { value: 'approved', label: 'Одобрен', icon: 'pi pi-check-circle' },
  { value: 'released', label: 'Выдан', icon: 'pi pi-send' }
]

// Вычисляемые свойства для графиков
const testTypeChartData = computed(() => {
  const types = {}
  testResults.value.forEach(test => {
    const label = getTestTypeLabel(test.test_type)
    types[label] = (types[label] || 0) + 1
  })

  return {
    labels: Object.keys(types),
    datasets: [{
      data: Object.values(types),
      backgroundColor: [
        '#42A5F5',
        '#66BB6A',
        '#FFA726',
        '#AB47BC',
        '#EC407A'
      ]
    }]
  }
})

const testResultChartData = computed(() => {
  const passed = testResults.value.filter(t => t.pass_fail === 'PASS').length
  const failed = testResults.value.filter(t => t.pass_fail === 'FAIL').length

  return {
    labels: ['Пройдено', 'Не пройдено'],
    datasets: [{
      label: 'Результаты',
      data: [passed, failed],
      backgroundColor: ['#4CAF50', '#F44336']
    }]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}

// Методы
const loadTestResults = async () => {
  try {
    loadingTests.value = true
    testResults.value = await testService.getByMaterialId(props.material.id)
  } catch (error) {
    console.error('Ошибка загрузки результатов испытаний:', error)
  } finally {
    loadingTests.value = false
  }
}

const loadDocuments = async () => {
  try {
    documents.value = await documentService.getByMaterialId(props.material.id)
  } catch (error) {
    console.error('Ошибка загрузки документов:', error)
  }
}

const loadWorkflowHistory = async () => {
  try {
    workflowHistory.value = await materialService.getHistory(props.material.id)
  } catch (error) {
    console.error('Ошибка загрузки истории:', error)
  }
}

const loadAvailableTransitions = async () => {
  try {
    availableTransitions.value = await materialService.getAvailableTransitions(props.material.id)
  } catch (error) {
    console.error('Ошибка загрузки переходов:', error)
  }
}

const loadUsers = async () => {
  try {
    const userList = await userService.getAll()
    userList.forEach(user => {
      users.value[user.id] = user
    })
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  }
}

const onTestAdded = () => {
  showAddTestDialog.value = false
  loadTestResults()
  toast.add({
    severity: 'success',
    summary: 'Успешно',
    detail: 'Результат испытания добавлен',
    life: 3000
  })
}

const viewTestDetails = (test) => {
  selectedTest.value = test
  showTestDetailsDialog.value = true
}

const downloadTestReport = async (test) => {
  try {
    await testService.downloadReport(test.id)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Отчет загружен',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить отчет',
      life: 5000
    })
  }
}

const onFileUpload = async (event) => {
  try {
    await documentService.upload(props.material.id, event.files[0])
    showUploadDialog.value = false
    loadDocuments()
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Документ загружен',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить документ',
      life: 5000
    })
  }
}

const downloadDocument = async (doc) => {
  try {
    await documentService.download(doc.id)
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось скачать документ',
      life: 5000
    })
  }
}

const previewDocument = (doc) => {
  window.open(doc.url, '_blank')
}

const deleteDocument = async (doc) => {
  try {
    await documentService.delete(doc.id)
    loadDocuments()
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Документ удален',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось удалить документ',
      life: 5000
    })
  }
}

const executeTransition = (transition) => {
  selectedTransition.value = transition
  transitionNotes.value = ''
  showTransitionDialog.value = true
}

const confirmTransition = async () => {
  try {
    await materialService.changeStatus(
      props.material.id,
      selectedTransition.value.to,
      transitionNotes.value
    )
    showTransitionDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Статус изменен',
      life: 3000
    })
    // Обновляем данные
    loadWorkflowHistory()
    loadAvailableTransitions()
    // Обновляем статус в родительском компоненте
    props.material.status = selectedTransition.value.to
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось изменить статус',
      life: 5000
    })
  }
}

const isStepCompleted = (step) => {
  const stepOrder = ['received', 'quarantine', 'testing', 'approved', 'released']
  const currentIndex = stepOrder.indexOf(props.material.status)
  const stepIndex = stepOrder.indexOf(step)
  return stepIndex < currentIndex
}

// Вспомогательные функции
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('ru-RU')
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getUserName = (userId) => {
  const user = users.value[userId]
  return user ? `${user.first_name} ${user.last_name}` : 'Неизвестный'
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
  return icons[status] || 'pi pi-circle'
}

const getStatusColor = (status) => {
  const colors = {
    'received': '#2196F3',
    'quarantine': '#FF9800',
    'testing': '#9C27B0',
    'approved': '#4CAF50',
    'released': '#00BCD4',
    'rejected': '#F44336'
  }
  return colors[status] || '#9E9E9E'
}

const getTypeLabel = (type) => {
  const labels = {
    'sheet': 'Листовой прокат',
    'profile': 'Сортовой прокат',
    'pipe': 'Трубы',
    'wire': 'Проволока',
    'rebar': 'Арматура',
    'other': 'Прочее'
  }
  return labels[type] || type
}

const getTestTypeLabel = (type) => {
  const labels = {
    'chemical': 'Химический анализ',
    'tensile': 'Испытания на растяжение',
    'impact': 'Испытания на удар',
    'hardness': 'Измерение твердости',
    'ultrasonic': 'Ультразвуковой контроль',
    'magnetic': 'Магнитопорошковый контроль',
    'visual': 'Визуальный контроль',
    'thickness': 'Измерение толщины',
    'metallography': 'Металлография'
  }
  return labels[type] || type
}

const getDocumentIcon = (type) => {
  if (type?.includes('pdf')) return 'pi pi-file-pdf text-red-500'
  if (type?.includes('image')) return 'pi pi-image text-blue-500'
  if (type?.includes('word')) return 'pi pi-file-word text-blue-600'
  if (type?.includes('excel')) return 'pi pi-file-excel text-green-600'
  return 'pi pi-file text-gray-500'
}

// Хук жизненного цикла
onMounted(() => {
  loadTestResults()
  loadDocuments()
  loadWorkflowHistory()
  loadAvailableTransitions()
  loadUsers()
})
</script>

<style scoped>
.material-detail {
  padding: 1rem;
}

/* Информационная секция */
.info-section {
  padding: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.info-group {
  display: flex;
  flex-direction: column;
}

.info-group label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.info-group .value {
  color: var(--text-color);
}

.notes-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 6px;
}

.notes-text {
  margin-top: 0.5rem;
  color: var(--text-color);
}

/* Секция испытаний */
.tests-section {
  padding: 1rem;
}

.tests-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.test-charts {
  margin-top: 2rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.chart-container {
  height: 300px;
}

.chart-container h5 {
  margin-bottom: 1rem;
  color: var(--text-color);
}

/* Секция документов */
.documents-section {
  padding: 1rem;
}

.documents-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.document-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.document-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.document-icon {
  margin-right: 1rem;
}

.document-info {
  flex: 1;
}

.document-info h5 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: var(--text-color);
}

.document-actions {
  display: flex;
  gap: 0.25rem;
}

/* Секция истории */
.history-section {
  padding: 1rem;
}

.timeline-marker {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

/* Секция workflow */
.workflow-section {
  padding: 1rem;
}

.current-status {
  text-align: center;
  margin-bottom: 2rem;
}

.status-display {
  margin-top: 1rem;
}

.transitions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.transition-card {
  padding: 1.5rem;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.transition-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.transition-info h5 {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.workflow-visualization {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  position: relative;
}

.workflow-visualization::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 2px;
  background: var(--surface-border);
  z-index: 0;
}

.workflow-step {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  z-index: 1;
}

.step-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--surface-100);
  border: 2px solid var(--surface-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--text-color-secondary);
  transition: all 0.3s;
}

.workflow-step.completed .step-icon {
  background: var(--green-100);
  border-color: var(--green-500);
  color: var(--green-700);
}

.workflow-step.active .step-icon {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
  transform: scale(1.2);
}

.step-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  text-align: center;
  max-width: 100px;
}

.workflow-step.active .step-label {
  font-weight: 600;
  color: var(--primary-color);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-color-secondary);
}

/* Диалог перехода */
.transition-form .field {
  margin-bottom: 1rem;
}

.transition-form label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

/* Адаптивность */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .documents-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .workflow-visualization {
    flex-direction: column;
    gap: 2rem;
  }

  .workflow-visualization::before {
    top: 10%;
    bottom: 10%;
    left: 50%;
    right: auto;
    width: 2px;
    height: auto;
  }
}
</style>