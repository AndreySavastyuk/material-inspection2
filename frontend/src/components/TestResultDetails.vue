<template>
  <div class="test-result-details">
    <div v-if="test">
      <!-- Основная информация -->
      <div class="info-header">
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">Испытание №{{ test.test_id }}</h2>
            <p class="text-secondary mt-2">
              Создано: {{ formatDateTime(test.created_at) }}
            </p>
          </div>
          <div class="flex gap-2">
            <Tag :value="getStatusLabel(test.status)" :severity="getStatusSeverity(test.status)" />
            <Tag :value="getPriorityLabel(test.priority)" :severity="getPrioritySeverity(test.priority)" />
            <Tag v-if="test.results?.pass_fail"
                 :value="test.results.pass_fail === 'PASS' ? 'Соответствует' : 'Не соответствует'"
                 :severity="test.results.pass_fail === 'PASS' ? 'success' : 'danger'" />
          </div>
        </div>
      </div>

      <Divider />

      <!-- Табы с информацией -->
      <TabView>
        <!-- Общая информация -->
        <TabPanel header="Общая информация">
          <div class="grid">
            <div class="col-6">
              <h4>Материал</h4>
              <div class="info-block">
                <p><strong>Код:</strong> {{ test.material?.material_code }}</p>
                <p><strong>Название:</strong> {{ test.material?.name }}</p>
                <p><strong>Марка:</strong> {{ test.material?.grade }}</p>
                <p><strong>Поставщик:</strong> {{ test.material?.supplier }}</p>
              </div>
            </div>

            <div class="col-6">
              <h4>Параметры испытания</h4>
              <div class="info-block">
                <p><strong>Тип:</strong> {{ getTestTypeLabel(test.test_type) }}</p>
                <p><strong>Метод:</strong> {{ getTestMethodLabel(test.test_method) }}</p>
                <p><strong>Категория:</strong> {{ getTestCategoryLabel(test.test_category) }}</p>
                <p><strong>Приоритет:</strong> {{ getPriorityLabel(test.priority) }}</p>
              </div>
            </div>

            <div class="col-6">
              <h4>Исполнение</h4>
              <div class="info-block">
                <p><strong>Ответственный:</strong> {{ test.assigned_to_user?.full_name || 'Не назначен' }}</p>
                <p><strong>Запланировано:</strong> {{ formatDate(test.scheduled_date) }}</p>
                <p><strong>Выполнено:</strong> {{ formatDate(test.completed_at) || 'В процессе' }}</p>
                <p><strong>Длительность:</strong> {{ calculateDuration() }}</p>
              </div>
            </div>

            <div class="col-6">
              <h4>Стандарты</h4>
              <div class="info-block">
                <div v-if="test.required_standards?.length">
                  <Chip v-for="standard in test.required_standards"
                        :key="standard"
                        :label="standard"
                        class="mr-2 mb-2" />
                </div>
                <p v-else class="text-secondary">Стандарты не указаны</p>
              </div>
            </div>

            <div v-if="test.notes" class="col-12">
              <h4>Примечания</h4>
              <div class="info-block">
                <p>{{ test.notes }}</p>
              </div>
            </div>
          </div>
        </TabPanel>

        <!-- Результаты испытания -->
        <TabPanel header="Результаты" :disabled="!test.results">
          <div v-if="test.results" class="results-content">
            <!-- Общий результат -->
            <div class="result-summary mb-4">
              <Card>
                <template #content>
                  <div class="flex justify-content-between align-items-center">
                    <div>
                      <h3 class="m-0">Результат испытания</h3>
                      <p class="text-secondary mt-2">
                        Дата проведения: {{ formatDate(test.results.test_date) }}
                      </p>
                    </div>
                    <div>
                      <Tag :value="test.results.pass_fail === 'PASS' ? 'СООТВЕТСТВУЕТ' : 'НЕ СООТВЕТСТВУЕТ'"
                           :severity="test.results.pass_fail === 'PASS' ? 'success' : 'danger'"
                           style="font-size: 1.2rem; padding: 0.75rem 1.5rem;" />
                    </div>
                  </div>
                </template>
              </Card>
            </div>

            <!-- Результаты по типу испытания -->
            <div class="specific-results">
              <!-- Механические испытания -->
              <div v-if="test.test_type === 'mechanical'" class="grid">
                <div class="col-12">
                  <h4>Механические характеристики</h4>
                </div>
                <div class="col-6 md:col-3">
                  <div class="result-item">
                    <label>Предел прочности</label>
                    <div class="result-value">
                      {{ test.results.tensile_strength || '—' }}
                      <span class="result-unit">МПа</span>
                    </div>
                  </div>
                </div>
                <div class="col-6 md:col-3">
                  <div class="result-item">
                    <label>Предел текучести</label>
                    <div class="result-value">
                      {{ test.results.yield_strength || '—' }}
                      <span class="result-unit">МПа</span>
                    </div>
                  </div>
                </div>
                <div class="col-6 md:col-3">
                  <div class="result-item">
                    <label>Относительное удлинение</label>
                    <div class="result-value">
                      {{ test.results.elongation || '—' }}
                      <span class="result-unit">%</span>
                    </div>
                  </div>
                </div>
                <div class="col-6 md:col-3">
                  <div class="result-item">
                    <label>Твердость</label>
                    <div class="result-value">
                      {{ test.results.hardness || '—' }}
                      <span class="result-unit">HB</span>
                    </div>
                  </div>
                </div>
                <div v-if="test.results.impact_strength" class="col-6 md:col-3">
                  <div class="result-item">
                    <label>Ударная вязкость</label>
                    <div class="result-value">
                      {{ test.results.impact_strength }}
                      <span class="result-unit">Дж/см²</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Химический анализ -->
              <div v-else-if="test.test_type === 'chemical'" class="grid">
                <div class="col-12">
                  <h4>Химический состав, %</h4>
                </div>
                <div v-for="(value, element) in test.results.chemical_composition"
                     :key="element"
                     class="col-4 md:col-2">
                  <div class="result-item">
                    <label>{{ element }}</label>
                    <div class="result-value">{{ value || '—' }}</div>
                  </div>
                </div>
              </div>

              <!-- Визуальный контроль -->
              <div v-else-if="test.test_type === 'visual'" class="grid">
                <div class="col-12">
                  <h4>Результаты визуального контроля</h4>
                </div>
                <div class="col-6">
                  <div class="result-item">
                    <label>Качество поверхности</label>
                    <div class="result-value">
                      {{ getSurfaceQualityLabel(test.results.surface_quality) }}
                    </div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="result-item">
                    <label>Обнаружены дефекты</label>
                    <div class="result-value">
                      <Tag :value="test.results.defects_found === 'true' ? 'Да' : 'Нет'"
                           :severity="test.results.defects_found === 'true' ? 'danger' : 'success'" />
                    </div>
                  </div>
                </div>
                <div v-if="test.results.defects_found === 'true'" class="col-12">
                  <div class="result-item">
                    <label>Описание дефектов</label>
                    <p>{{ test.results.defect_description }}</p>
                    <div v-if="test.results.defect_types?.length" class="mt-2">
                      <Chip v-for="defect in test.results.defect_types"
                            :key="defect"
                            :label="getDefectTypeLabel(defect)"
                            severity="warning"
                            class="mr-2" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Геометрические измерения -->
              <div v-else-if="test.test_type === 'dimensional'" class="grid">
                <div class="col-12">
                  <h4>Геометрические параметры</h4>
                </div>
                <div class="col-4">
                  <div class="result-item">
                    <label>Толщина</label>
                    <div class="result-value">
                      {{ test.results.thickness || '—' }}
                      <span class="result-unit">мм</span>
                    </div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="result-item">
                    <label>Ширина</label>
                    <div class="result-value">
                      {{ test.results.width || '—' }}
                      <span class="result-unit">мм</span>
                    </div>
                  </div>
                </div>
                <div class="col-4">
                  <div class="result-item">
                    <label>Длина</label>
                    <div class="result-value">
                      {{ test.results.length || '—' }}
                      <span class="result-unit">мм</span>
                    </div>
                  </div>
                </div>
                <div v-if="test.results.flatness" class="col-6">
                  <div class="result-item">
                    <label>Плоскостность</label>
                    <div class="result-value">
                      {{ test.results.flatness }}
                      <span class="result-unit">мм</span>
                    </div>
                  </div>
                </div>
                <div v-if="test.results.roughness" class="col-6">
                  <div class="result-item">
                    <label>Шероховатость</label>
                    <div class="result-value">
                      Ra {{ test.results.roughness }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Примечания к результатам -->
            <div v-if="test.results.notes" class="mt-4">
              <h4>Примечания к результатам</h4>
              <Card>
                <template #content>
                  <p>{{ test.results.notes }}</p>
                </template>
              </Card>
            </div>

            <!-- Сравнение со стандартами -->
            <div v-if="standardsComparison" class="mt-4">
              <h4>Соответствие стандартам</h4>
              <DataTable :value="standardsComparison" responsiveLayout="scroll">
                <Column field="parameter" header="Параметр" />
                <Column field="standard" header="Стандарт" />
                <Column field="requirement" header="Требование" />
                <Column field="actual" header="Фактическое" />
                <Column field="result" header="Результат">
                  <template #body="slotProps">
                    <Tag :value="slotProps.data.result"
                         :severity="slotProps.data.result === 'Соответствует' ? 'success' : 'danger'" />
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>

          <div v-else class="p-4">
            <Message severity="info" :closable="false">
              Результаты испытания еще не добавлены
            </Message>
          </div>
        </TabPanel>

        <!-- Документы и файлы -->
        <TabPanel header="Документы">
          <div class="documents-section">
            <div v-if="test.attachments?.length" class="grid">
              <div v-for="doc in test.attachments" :key="doc.id" class="col-12 md:col-6 lg:col-4">
                <Card>
                  <template #content>
                    <div class="document-item">
                      <i :class="getDocumentIcon(doc.type)" class="text-3xl mb-2"></i>
                      <h5>{{ doc.name }}</h5>
                      <p class="text-secondary">{{ formatFileSize(doc.size) }}</p>
                      <div class="flex gap-2 mt-3">
                        <Button label="Скачать" icon="pi pi-download" size="small" @click="downloadDocument(doc)" />
                        <Button label="Просмотр" icon="pi pi-eye" size="small" severity="secondary" @click="previewDocument(doc)" />
                      </div>
                    </div>
                  </template>
                </Card>
              </div>
            </div>
            <div v-else>
              <Message severity="info" :closable="false">
                Документы не приложены
              </Message>
            </div>
          </div>
        </TabPanel>

        <!-- История действий -->
        <TabPanel header="История">
          <Timeline :value="testHistory">
            <template #content="slotProps">
              <Card>
                <template #content>
                  <div class="timeline-event">
                    <div class="flex justify-content-between">
                      <h5 class="m-0">{{ slotProps.item.action }}</h5>
                      <span class="text-secondary">{{ formatDateTime(slotProps.item.date) }}</span>
                    </div>
                    <p class="mt-2 mb-0">
                      <strong>{{ slotProps.item.user }}</strong>
                      <span v-if="slotProps.item.details" class="ml-2">— {{ slotProps.item.details }}</span>
                    </p>
                  </div>
                </template>
              </Card>
            </template>
          </Timeline>
        </TabPanel>
      </TabView>

      <!-- Панель действий -->
      <div class="action-panel mt-4">
        <div class="flex justify-content-between">
          <div class="flex gap-2">
            <Button
              label="Печать протокола"
              icon="pi pi-print"
              @click="printProtocol"
              severity="secondary"
            />
            <Button
              label="Экспорт PDF"
              icon="pi pi-file-pdf"
              @click="exportPDF"
              severity="secondary"
            />
            <Button
              label="Экспорт Excel"
              icon="pi pi-file-excel"
              @click="exportExcel"
              severity="secondary"
            />
          </div>
          <div class="flex gap-2">
            <Button
              v-if="canApprove"
              label="Утвердить результаты"
              icon="pi pi-check"
              @click="approveResults"
              severity="success"
            />
            <Button
              v-if="canEdit"
              label="Редактировать"
              icon="pi pi-pencil"
              @click="$emit('edit', test)"
            />
          </div>
        </div>
      </div>
    </div>

    <div v-else class="p-4">
      <Message severity="warn" :closable="false">
        Испытание не выбрано
      </Message>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { testService } from '@/services/testService'
import { useAuthStore } from '@/stores/authStore'

const props = defineProps({
  test: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'approve', 'export'])

const toast = useToast()
const authStore = useAuthStore()

// Данные
const testHistory = ref([])
const standardsComparison = ref(null)

// Вычисляемые свойства
const canEdit = computed(() => {
  return authStore.user?.role === 'lab_manager' ||
         authStore.user?.id === props.test?.assigned_to
})

const canApprove = computed(() => {
  return authStore.user?.role === 'lab_manager' &&
         props.test?.status === 'completed' &&
         !props.test?.approved_at
})

// Вспомогательные функции
const getStatusLabel = (status) => {
  const labels = {
    pending: 'Ожидает',
    in_progress: 'В процессе',
    completed: 'Завершено',
    cancelled: 'Отменено'
  }
  return labels[status] || status
}

const getStatusSeverity = (status) => {
  const severities = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'secondary'
  }
  return severities[status] || 'secondary'
}

const getPriorityLabel = (priority) => {
  const labels = {
    low: 'Низкий',
    normal: 'Обычный',
    high: 'Высокий',
    urgent: 'Срочный'
  }
  return labels[priority] || priority
}

const getPrioritySeverity = (priority) => {
  const severities = {
    low: 'secondary',
    normal: 'info',
    high: 'warning',
    urgent: 'danger'
  }
  return severities[priority] || 'secondary'
}

const getTestTypeLabel = (type) => {
  const labels = {
    mechanical: 'Механические испытания',
    chemical: 'Химический анализ',
    visual: 'Визуальный контроль',
    dimensional: 'Геометрические измерения',
    metallography: 'Металлография'
  }
  return labels[type] || type
}

const getTestMethodLabel = (method) => {
  const labels = {
    tensile: 'Растяжение',
    hardness: 'Твердость',
    impact: 'Ударная вязкость',
    spectral: 'Спектральный анализ',
    visual: 'Визуальный осмотр',
    geometry: 'Измерение геометрии'
  }
  return labels[method] || method
}

const getTestCategoryLabel = (category) => {
  const labels = {
    incoming: 'Входной контроль',
    periodic: 'Периодический контроль',
    arbitration: 'Арбитражный контроль',
    unscheduled: 'Внеплановый контроль'
  }
  return labels[category] || category
}

const getSurfaceQualityLabel = (quality) => {
  const labels = {
    excellent: 'Отличное',
    good: 'Хорошее',
    satisfactory: 'Удовлетворительное',
    unsatisfactory: 'Неудовлетворительное'
  }
  return labels[quality] || quality
}

const getDefectTypeLabel = (defect) => {
  const labels = {
    scratches: 'Царапины',
    dents: 'Вмятины',
    corrosion: 'Коррозия',
    cracks: 'Трещины',
    cavities: 'Раковины',
    inclusions: 'Включения',
    delamination: 'Расслоение',
    other: 'Прочие'
  }
  return labels[defect] || defect
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('ru-RU')
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getDocumentIcon = (type) => {
  if (type?.includes('pdf')) return 'pi pi-file-pdf text-red-500'
  if (type?.includes('image')) return 'pi pi-image text-blue-500'
  if (type?.includes('word')) return 'pi pi-file-word text-blue-600'
  if (type?.includes('excel')) return 'pi pi-file-excel text-green-600'
  return 'pi pi-file text-gray-500'
}

const calculateDuration = () => {
  if (!props.test?.scheduled_date || !props.test?.completed_at) {
    return 'Не завершено'
  }
  const start = new Date(props.test.scheduled_date)
  const end = new Date(props.test.completed_at)
  const days = Math.floor((end - start) / (1000 * 60 * 60 * 24))
  return `${days} дней`
}

// Загрузка данных
const loadTestHistory = () => {
  // Заглушка для истории
  testHistory.value = [
    {
      date: props.test?.created_at,
      action: 'Испытание создано',
      user: 'Система',
      details: 'Инициализация испытания'
    },
    {
      date: props.test?.scheduled_date,
      action: 'Назначено исполнителю',
      user: 'Иванов И.И.',
      details: props.test?.assigned_to_user?.full_name
    }
  ]

  if (props.test?.status === 'completed') {
    testHistory.value.push({
      date: props.test?.completed_at,
      action: 'Результаты добавлены',
      user: props.test?.assigned_to_user?.full_name,
      details: 'Испытание завершено'
    })
  }
}

const loadStandardsComparison = () => {
  // Заглушка для сравнения со стандартами
  if (props.test?.test_type === 'mechanical' && props.test?.results) {
    standardsComparison.value = [
      {
        parameter: 'Предел прочности',
        standard: 'ГОСТ 1497-84',
        requirement: '≥ 470 МПа',
        actual: `${props.test.results.tensile_strength} МПа`,
        result: props.test.results.tensile_strength >= 470 ? 'Соответствует' : 'Не соответствует'
      },
      {
        parameter: 'Предел текучести',
        standard: 'ГОСТ 1497-84',
        requirement: '≥ 325 МПа',
        actual: `${props.test.results.yield_strength} МПа`,
        result: props.test.results.yield_strength >= 325 ? 'Соответствует' : 'Не соответствует'
      },
      {
        parameter: 'Относительное удлинение',
        standard: 'ГОСТ 1497-84',
        requirement: '≥ 21%',
        actual: `${props.test.results.elongation}%`,
        result: props.test.results.elongation >= 21 ? 'Соответствует' : 'Не соответствует'
      }
    ]
  }
}

// Действия
const printProtocol = () => {
  window.print()
}

const exportPDF = async () => {
  try {
    await testService.downloadReport(props.test.id)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Протокол экспортирован в PDF'
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось экспортировать протокол'
    })
  }
}

const exportExcel = () => {
  emit('export', 'excel')
}

const approveResults = async () => {
  try {
    await testService.approve(props.test.id, {
      approved_by: authStore.user.id,
      notes: 'Результаты проверены и утверждены'
    })
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Результаты испытания утверждены'
    })
    emit('approve', props.test)
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось утвердить результаты'
    })
  }
}

const downloadDocument = (doc) => {
  // Логика скачивания документа
  console.log('Download document:', doc)
}

const previewDocument = (doc) => {
  // Логика предпросмотра документа
  window.open(doc.url, '_blank')
}

// Инициализация
onMounted(() => {
  loadTestHistory()
  loadStandardsComparison()
})
</script>

<style scoped>
.test-result-details {
  padding: 1rem;
}

.info-header {
  margin-bottom: 1.5rem;
}

.info-header h2 {
  color: var(--primary-color);
}

.info-block {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: 6px;
}

.info-block p {
  margin: 0.5rem 0;
}

.result-summary {
  margin-bottom: 2rem;
}

.result-item {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 1rem;
}

.result-item label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.5rem;
}

.result-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
}

.result-unit {
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--text-color-secondary);
  margin-left: 0.25rem;
}

.document-item {
  text-align: center;
  padding: 1rem;
}

.document-item h5 {
  margin: 0.5rem 0;
  word-break: break-word;
}

.timeline-event {
  padding: 0.5rem;
}

.action-panel {
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 6px;
}

h3, h4 {
  color: var(--primary-color);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.text-secondary {
  color: var(--text-color-secondary);
}
</style>