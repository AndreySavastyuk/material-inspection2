<template>
  <div class="test-results-view">
    <!-- Заголовок -->
    <div class="page-header">
      <div class="header-content">
        <h1><i class="pi pi-chart-line mr-2"></i>Результаты испытаний</h1>
        <p class="text-secondary">Управление лабораторными испытаниями и контролем качества</p>
      </div>
      <div class="header-actions">
        <Button
          label="Экспорт отчета"
          icon="pi pi-file-pdf"
          severity="secondary"
          outlined
          @click="exportReport"
          class="mr-2"
        />
        <Button
          label="Новое испытание"
          icon="pi pi-plus"
          severity="success"
          @click="showNewTestDialog = true"
        />
      </div>
    </div>

    <!-- Статистика -->
    <div class="statistics-cards">
      <div class="stat-card">
        <div class="stat-icon bg-blue-100">
          <i class="pi pi-flask text-blue-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Всего испытаний</span>
          <span class="stat-value">{{ statistics.total }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-orange-100">
          <i class="pi pi-clock text-orange-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">В процессе</span>
          <span class="stat-value">{{ statistics.inProgress }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-green-100">
          <i class="pi pi-check-circle text-green-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Пройдено</span>
          <span class="stat-value">{{ statistics.passed }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon bg-red-100">
          <i class="pi pi-times-circle text-red-600"></i>
        </div>
        <div class="stat-content">
          <span class="stat-label">Не пройдено</span>
          <span class="stat-value">{{ statistics.failed }}</span>
        </div>
      </div>
    </div>

    <!-- Фильтры и таблица -->
    <div class="content-grid">
      <!-- Левая панель с фильтрами -->
      <Card class="filters-panel">
        <template #title>
          <i class="pi pi-filter mr-2"></i>
          Фильтры
        </template>
        <template #content>
          <div class="filter-section">
            <label>Поиск</label>
            <InputText
              v-model="filters.search"
              placeholder="Код материала или испытание..."
              @input="onFilterChange"
              class="w-full"
            />
          </div>

          <div class="filter-section">
            <label>Период</label>
            <Calendar
              v-model="filters.dateRange"
              selectionMode="range"
              dateFormat="dd.mm.yy"
              @date-select="onFilterChange"
              showIcon
              class="w-full"
            />
          </div>

          <div class="filter-section">
            <label>Тип испытания</label>
            <MultiSelect
              v-model="filters.testTypes"
              :options="testTypeOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Все типы"
              @change="onFilterChange"
              class="w-full"
              display="chip"
            />
          </div>

          <div class="filter-section">
            <label>Категория</label>
            <SelectButton
              v-model="filters.category"
              :options="categoryOptions"
              optionLabel="label"
              optionValue="value"
              @change="onFilterChange"
              class="w-full"
            />
          </div>

          <div class="filter-section">
            <label>Результат</label>
            <SelectButton
              v-model="filters.result"
              :options="resultOptions"
              optionLabel="label"
              optionValue="value"
              @change="onFilterChange"
              class="w-full"
            />
          </div>

          <div class="filter-section">
            <label>Исполнитель</label>
            <Dropdown
              v-model="filters.tester"
              :options="testers"
              optionLabel="name"
              optionValue="id"
              placeholder="Все исполнители"
              @change="onFilterChange"
              class="w-full"
              filter
            />
          </div>

          <Button
            label="Сбросить фильтры"
            icon="pi pi-times"
            severity="secondary"
            text
            @click="resetFilters"
            class="w-full mt-3"
          />
        </template>
      </Card>

      <!-- Основная область с таблицей -->
      <div class="main-content">
        <!-- Быстрые действия -->
        <Card class="mb-3">
          <template #content>
            <div class="quick-actions">
              <Button
                label="Ожидают испытаний"
                icon="pi pi-exclamation-triangle"
                severity="warning"
                text
                @click="showPendingTests"
                :badge="pendingCount"
                badgeSeverity="warning"
              />
              <Button
                label="Требуют повторного испытания"
                icon="pi pi-refresh"
                severity="danger"
                text
                @click="showRetestRequired"
                :badge="retestCount"
                badgeSeverity="danger"
              />
              <Button
                label="Истекает срок действия"
                icon="pi pi-calendar-times"
                severity="info"
                text
                @click="showExpiringTests"
                :badge="expiringCount"
                badgeSeverity="info"
              />
            </div>
          </template>
        </Card>

        <!-- Таблица результатов -->
        <Card>
          <template #content>
            <DataTable
              :value="testResults"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[10, 20, 50]"
              :loading="loading"
              responsiveLayout="scroll"
              stripedRows
              :rowHover="true"
              v-model:selection="selectedTests"
              @row-click="onRowClick"
              :rowClass="getRowClass"
            >
              <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>

              <Column field="test_id" header="ID" sortable style="min-width: 80px">
                <template #body="slotProps">
                  <span class="font-mono">{{ slotProps.data.test_id }}</span>
                </template>
              </Column>

              <Column field="material_code" header="Материал" sortable style="min-width: 140px">
                <template #body="slotProps">
                  <div>
                    <span class="font-semibold">{{ slotProps.data.material_code }}</span>
                    <br>
                    <small class="text-secondary">{{ slotProps.data.material_name }}</small>
                  </div>
                </template>
              </Column>

              <Column field="test_type" header="Тип испытания" sortable style="min-width: 180px">
                <template #body="slotProps">
                  <div class="test-type-cell">
                    <i :class="getTestTypeIcon(slotProps.data.test_type)" class="mr-2"></i>
                    {{ getTestTypeLabel(slotProps.data.test_type) }}
                  </div>
                </template>
              </Column>

              <Column field="test_category" header="Категория" sortable style="min-width: 140px">
                <template #body="slotProps">
                  <Tag
                    :value="slotProps.data.test_category === 'destructive' ? 'Разрушающий' : 'Неразрушающий'"
                    :severity="slotProps.data.test_category === 'destructive' ? 'danger' : 'info'"
                  />
                </template>
              </Column>

              <Column field="tested_at" header="Дата проведения" sortable style="min-width: 140px">
                <template #body="slotProps">
                  <span>{{ formatDate(slotProps.data.tested_at) }}</span>
                </template>
              </Column>

              <Column field="pass_fail" header="Результат" sortable style="min-width: 120px">
                <template #body="slotProps">
                  <Tag
                    v-if="slotProps.data.pass_fail"
                    :value="slotProps.data.pass_fail === 'PASS' ? 'Пройдено' : 'Не пройдено'"
                    :severity="slotProps.data.pass_fail === 'PASS' ? 'success' : 'danger'"
                    :icon="slotProps.data.pass_fail === 'PASS' ? 'pi pi-check' : 'pi pi-times'"
                  />
                  <Tag v-else value="В процессе" severity="warning" icon="pi pi-clock" />
                </template>
              </Column>

              <Column field="tested_by" header="Исполнитель" style="min-width: 150px">
                <template #body="slotProps">
                  <div class="tester-cell">
                    <Avatar
                      :label="getUserInitials(slotProps.data.tested_by_name)"
                      size="small"
                      shape="circle"
                      class="mr-2"
                    />
                    <span>{{ slotProps.data.tested_by_name }}</span>
                  </div>
                </template>
              </Column>

              <Column header="Действия" style="min-width: 150px">
                <template #body="slotProps">
                  <div class="actions-cell">
                    <Button
                      icon="pi pi-eye"
                      size="small"
                      text
                      rounded
                      @click.stop="viewTestDetails(slotProps.data)"
                      v-tooltip="'Просмотр'"
                    />
                    <Button
                      icon="pi pi-pencil"
                      size="small"
                      text
                      rounded
                      @click.stop="editTest(slotProps.data)"
                      v-tooltip="'Редактировать'"
                      :disabled="slotProps.data.pass_fail !== null"
                    />
                    <Button
                      icon="pi pi-file-pdf"
                      size="small"
                      text
                      rounded
                      @click.stop="generateReport(slotProps.data)"
                      v-tooltip="'Отчет'"
                    />
                    <Button
                      icon="pi pi-refresh"
                      size="small"
                      text
                      rounded
                      severity="warning"
                      @click.stop="retestMaterial(slotProps.data)"
                      v-tooltip="'Повторное испытание'"
                      v-if="slotProps.data.pass_fail === 'FAIL'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>

            <!-- Массовые действия -->
            <div v-if="selectedTests.length > 0" class="bulk-actions">
              <span class="mr-3">Выбрано: {{ selectedTests.length }}</span>
              <Button
                label="Сгенерировать отчет"
                icon="pi pi-file-pdf"
                size="small"
                severity="secondary"
                @click="generateBulkReport"
              />
              <Button
                label="Экспорт в Excel"
                icon="pi pi-file-excel"
                size="small"
                severity="secondary"
                @click="exportToExcel"
                class="ml-2"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Диалог нового испытания -->
    <Dialog
      v-model:visible="showNewTestDialog"
      header="Новое испытание"
      :modal="true"
      :style="{ width: '800px' }"
      :maximizable="true"
    >
      <NewTestForm @saved="onTestCreated" @cancel="showNewTestDialog = false" />
    </Dialog>

    <!-- Диалог деталей испытания -->
    <Dialog
      v-model:visible="showDetailsDialog"
      :header="`Результаты испытания: ${selectedTest?.test_id}`"
      :modal="true"
      :style="{ width: '900px' }"
      :maximizable="true"
    >
      <TestResultDetails v-if="selectedTest" :test="selectedTest" />
    </Dialog>

    <!-- Диалог редактирования -->
    <Dialog
      v-model:visible="showEditDialog"
      header="Редактировать результаты испытания"
      :modal="true"
      :style="{ width: '700px' }"
    >
      <EditTestForm
        v-if="selectedTest"
        :test="selectedTest"
        @saved="onTestUpdated"
        @cancel="showEditDialog = false"
      />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { testService } from '@/services/testService'
import { userService } from '@/services/userService'
import NewTestForm from '@/components/NewTestForm.vue'
import EditTestForm from '@/components/EditTestForm.vue'
import TestResultDetails from '@/components/TestResultDetails.vue'

const toast = useToast()
const router = useRouter()

// Состояние
const loading = ref(false)
const testResults = ref([])
const selectedTests = ref([])
const selectedTest = ref(null)
const testers = ref([])

// Диалоги
const showNewTestDialog = ref(false)
const showDetailsDialog = ref(false)
const showEditDialog = ref(false)

// Статистика
const statistics = reactive({
  total: 0,
  inProgress: 0,
  passed: 0,
  failed: 0
})

// Счетчики для быстрых действий
const pendingCount = ref(0)
const retestCount = ref(0)
const expiringCount = ref(0)

// Фильтры
const filters = reactive({
  search: '',
  dateRange: null,
  testTypes: [],
  category: null,
  result: null,
  tester: null
})

// Опции для фильтров
const testTypeOptions = ref([
  { label: 'Химический анализ', value: 'chemical' },
  { label: 'Испытания на растяжение', value: 'tensile' },
  { label: 'Испытания на удар', value: 'impact' },
  { label: 'Измерение твердости', value: 'hardness' },
  { label: 'Ультразвуковой контроль', value: 'ultrasonic' },
  { label: 'Магнитопорошковый контроль', value: 'magnetic' },
  { label: 'Визуальный контроль', value: 'visual' },
  { label: 'Измерение толщины', value: 'thickness' },
  { label: 'Металлография', value: 'metallography' }
])

const categoryOptions = ref([
  { label: 'Все', value: null },
  { label: 'Разрушающие', value: 'destructive' },
  { label: 'Неразрушающие', value: 'non_destructive' }
])

const resultOptions = ref([
  { label: 'Все', value: null },
  { label: 'Пройдено', value: 'PASS' },
  { label: 'Не пройдено', value: 'FAIL' },
  { label: 'В процессе', value: 'IN_PROGRESS' }
])

// Методы
const loadTestResults = async () => {
  try {
    loading.value = true
    const response = await testService.getAll(filters)
    testResults.value = response.items || []
    updateStatistics()
    updateCounters()
  } catch (error) {
    console.error('Ошибка загрузки результатов:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить результаты испытаний',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const loadTesters = async () => {
  try {
    const users = await userService.getLabUsers()
    testers.value = users.map(u => ({
      id: u.id,
      name: `${u.first_name} ${u.last_name}`
    }))
  } catch (error) {
    console.error('Ошибка загрузки пользователей:', error)
  }
}

const updateStatistics = () => {
  statistics.total = testResults.value.length
  statistics.inProgress = testResults.value.filter(t => !t.pass_fail).length
  statistics.passed = testResults.value.filter(t => t.pass_fail === 'PASS').length
  statistics.failed = testResults.value.filter(t => t.pass_fail === 'FAIL').length
}

const updateCounters = async () => {
  try {
    const counters = await testService.getCounters()
    pendingCount.value = counters.pending || 0
    retestCount.value = counters.retest_required || 0
    expiringCount.value = counters.expiring || 0
  } catch (error) {
    console.error('Ошибка загрузки счетчиков:', error)
  }
}

const onFilterChange = () => {
  loadTestResults()
}

const resetFilters = () => {
  filters.search = ''
  filters.dateRange = null
  filters.testTypes = []
  filters.category = null
  filters.result = null
  filters.tester = null
  loadTestResults()
}

const onRowClick = (event) => {
  viewTestDetails(event.data)
}

const viewTestDetails = (test) => {
  selectedTest.value = test
  showDetailsDialog.value = true
}

const editTest = (test) => {
  selectedTest.value = test
  showEditDialog.value = true
}

const generateReport = async (test) => {
  try {
    await testService.generateReport(test.id)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Отчет сгенерирован',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось сгенерировать отчет',
      life: 5000
    })
  }
}

const retestMaterial = async (test) => {
  try {
    await testService.createRetest(test.material_id, test.test_type)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Создано повторное испытание',
      life: 3000
    })
    loadTestResults()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось создать повторное испытание',
      life: 5000
    })
  }
}

const generateBulkReport = async () => {
  try {
    const ids = selectedTests.value.map(t => t.id)
    await testService.generateBulkReport(ids)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Сгенерирован отчет для ${ids.length} испытаний`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось сгенерировать отчет',
      life: 5000
    })
  }
}

const exportToExcel = async () => {
  try {
    const ids = selectedTests.value.map(t => t.id)
    await testService.exportToExcel(ids)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Данные экспортированы в Excel',
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

const exportReport = async () => {
  try {
    await testService.exportFullReport(filters)
    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Отчет экспортирован',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось экспортировать отчет',
      life: 5000
    })
  }
}

const showPendingTests = () => {
  filters.result = 'IN_PROGRESS'
  loadTestResults()
}

const showRetestRequired = () => {
  // Фильтруем по неудачным тестам
  filters.result = 'FAIL'
  loadTestResults()
}

const showExpiringTests = () => {
  // Здесь можно добавить фильтр по дате истечения
  toast.add({
    severity: 'info',
    summary: 'В разработке',
    detail: 'Функция будет доступна в следующей версии',
    life: 3000
  })
}

const onTestCreated = () => {
  showNewTestDialog.value = false
  loadTestResults()
  toast.add({
    severity: 'success',
    summary: 'Успешно',
    detail: 'Испытание создано',
    life: 3000
  })
}

const onTestUpdated = () => {
  showEditDialog.value = false
  loadTestResults()
  toast.add({
    severity: 'success',
    summary: 'Успешно',
    detail: 'Результаты обновлены',
    life: 3000
  })
}

const getRowClass = (data) => {
  if (data.pass_fail === 'FAIL') {
    return 'row-failed'
  }
  if (!data.pass_fail) {
    return 'row-pending'
  }
  return null
}

// Вспомогательные функции
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('ru-RU')
}

const getUserInitials = (name) => {
  if (!name) return '?'
  const parts = name.split(' ')
  return parts.map(p => p[0]).join('').toUpperCase()
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

const getTestTypeIcon = (type) => {
  const icons = {
    'chemical': 'pi pi-fw pi-flask',
    'tensile': 'pi pi-fw pi-arrows-h',
    'impact': 'pi pi-fw pi-bolt',
    'hardness': 'pi pi-fw pi-shield',
    'ultrasonic': 'pi pi-fw pi-wifi',
    'magnetic': 'pi pi-fw pi-compass',
    'visual': 'pi pi-fw pi-eye',
    'thickness': 'pi pi-fw pi-ruler',
    'metallography': 'pi pi-fw pi-search-plus'
  }
  return icons[type] || 'pi pi-fw pi-question'
}

// Хук жизненного цикла
onMounted(() => {
  loadTestResults()
  loadTesters()
})
</script>

<style scoped>
.test-results-view {
  padding: 1.5rem;
}

/* Заголовок страницы */
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

/* Основная сетка */
.content-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
}

/* Панель фильтров */
.filters-panel {
  height: fit-content;
  position: sticky;
  top: 1.5rem;
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

/* Основная область */
.main-content {
  min-width: 0;
}

/* Быстрые действия */
.quick-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* Таблица */
.test-type-cell {
  display: flex;
  align-items: center;
}

.tester-cell {
  display: flex;
  align-items: center;
}

.actions-cell {
  display: flex;
  gap: 0.25rem;
}

/* Строки таблицы с особым стилем */
:deep(.row-failed) {
  background-color: rgba(244, 67, 54, 0.05) !important;
}

:deep(.row-pending) {
  background-color: rgba(255, 193, 7, 0.05) !important;
}

/* Массовые действия */
.bulk-actions {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
  border-top: 1px solid var(--surface-border);
  margin-top: -1px;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .filters-panel {
    position: static;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .statistics-cards {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    flex-direction: column;
  }

  .quick-actions .p-button {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>