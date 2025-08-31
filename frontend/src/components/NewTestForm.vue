<template>
  <div class="new-test-form">
    <Steps :model="steps" :activeIndex="activeStep" />

    <div class="form-content mt-4">
      <!-- Шаг 1: Выбор материала -->
      <div v-if="activeStep === 0" class="step-content">
        <h3>Выбор материала для испытания</h3>

        <div class="grid">
          <div class="col-12">
            <div class="field">
              <label for="material">Материал <span class="required"></span></label>
              <AutoComplete
                id="material"
                v-model="selectedMaterial"
                :suggestions="filteredMaterials"
                @complete="searchMaterial"
                :dropdown="true"
                field="display"
                placeholder="Начните вводить код или название материала"
                :class="{ 'p-invalid': errors.material }"
                class="w-full"
              >
                <template #option="slotProps">
                  <div class="material-option">
                    <div>
                      <strong>{{ slotProps.option.material_code }}</strong> - {{ slotProps.option.name }}
                    </div>
                    <div class="text-sm text-secondary">
                      {{ slotProps.option.material_type }} | {{ slotProps.option.supplier }}
                    </div>
                  </div>
                </template>
              </AutoComplete>
              <small v-if="errors.material" class="p-error">{{ errors.material }}</small>
            </div>
          </div>

          <div v-if="selectedMaterial && typeof selectedMaterial === 'object'" class="col-12">
            <Card>
              <template #title>Информация о материале</template>
              <template #content>
                <div class="grid">
                  <div class="col-6">
                    <p><strong>Код:</strong> {{ selectedMaterial.material_code }}</p>
                    <p><strong>Название:</strong> {{ selectedMaterial.name }}</p>
                    <p><strong>Марка:</strong> {{ selectedMaterial.grade }}</p>
                  </div>
                  <div class="col-6">
                    <p><strong>Тип:</strong> {{ selectedMaterial.material_type }}</p>
                    <p><strong>Поставщик:</strong> {{ selectedMaterial.supplier }}</p>
                    <p><strong>Статус:</strong>
                      <Tag :value="selectedMaterial.status" :severity="getMaterialStatusSeverity(selectedMaterial.status)" />
                    </p>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </div>

      <!-- Шаг 2: Параметры испытания -->
      <div v-if="activeStep === 1" class="step-content">
        <h3>Параметры испытания</h3>

        <div class="grid">
          <div class="col-6">
            <div class="field">
              <label for="test_type">Тип испытания <span class="required"></span></label>
              <Dropdown
                id="test_type"
                v-model="testForm.test_type"
                :options="testTypeOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите тип испытания"
                :class="{ 'p-invalid': errors.test_type }"
                @change="onTestTypeChange"
              />
              <small v-if="errors.test_type" class="p-error">{{ errors.test_type }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="test_method">Метод испытания <span class="required"></span></label>
              <Dropdown
                id="test_method"
                v-model="testForm.test_method"
                :options="getTestMethods(testForm.test_type)"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите метод"
                :disabled="!testForm.test_type"
                :class="{ 'p-invalid': errors.test_method }"
              />
              <small v-if="errors.test_method" class="p-error">{{ errors.test_method }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="test_category">Категория испытания</label>
              <Dropdown
                id="test_category"
                v-model="testForm.test_category"
                :options="testCategoryOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите категорию"
              />
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="priority">Приоритет <span class="required"></span></label>
              <SelectButton
                v-model="testForm.priority"
                :options="priorityOptions"
                optionLabel="label"
                optionValue="value"
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="standards">Стандарты испытаний</label>
              <MultiSelect
                id="standards"
                v-model="testForm.required_standards"
                :options="standardsOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите применимые стандарты"
                display="chip"
                filter
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="test_requirements">Требования к испытанию</label>
              <Textarea
                id="test_requirements"
                v-model="testForm.requirements"
                rows="3"
                placeholder="Укажите специальные требования или условия проведения испытания"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Шаг 3: Назначение и сроки -->
      <div v-if="activeStep === 2" class="step-content">
        <h3>Назначение исполнителя и сроки</h3>

        <div class="grid">
          <div class="col-6">
            <div class="field">
              <label for="assigned_to">Ответственный лаборант <span class="required"></span></label>
              <Dropdown
                id="assigned_to"
                v-model="testForm.assigned_to"
                :options="labUsers"
                optionLabel="full_name"
                optionValue="id"
                placeholder="Выберите лаборанта"
                :class="{ 'p-invalid': errors.assigned_to }"
                filter
              >
                <template #option="slotProps">
                  <div class="flex align-items-center">
                    <Avatar
                      :label="getInitials(slotProps.option.full_name)"
                      class="mr-2"
                      size="small"
                      :style="{ backgroundColor: getAvatarColor(slotProps.option.id) }"
                    />
                    <div>
                      <div>{{ slotProps.option.full_name }}</div>
                      <div class="text-sm text-secondary">{{ slotProps.option.position }}</div>
                    </div>
                  </div>
                </template>
              </Dropdown>
              <small v-if="errors.assigned_to" class="p-error">{{ errors.assigned_to }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="department">Подразделение</label>
              <InputText
                id="department"
                v-model="testForm.department"
                placeholder="ЦЗЛ"
                disabled
              />
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="scheduled_date">Планируемая дата испытания <span class="required"></span></label>
              <Calendar
                id="scheduled_date"
                v-model="testForm.scheduled_date"
                dateFormat="dd.mm.yy"
                :minDate="new Date()"
                showIcon
                :class="{ 'p-invalid': errors.scheduled_date }"
              />
              <small v-if="errors.scheduled_date" class="p-error">{{ errors.scheduled_date }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="deadline">Крайний срок</label>
              <Calendar
                id="deadline"
                v-model="testForm.deadline"
                dateFormat="dd.mm.yy"
                :minDate="testForm.scheduled_date"
                showIcon
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="equipment">Необходимое оборудование</label>
              <MultiSelect
                id="equipment"
                v-model="testForm.equipment"
                :options="equipmentOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите оборудование"
                display="chip"
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="notes">Примечания</label>
              <Textarea
                id="notes"
                v-model="testForm.notes"
                rows="3"
                placeholder="Дополнительные комментарии или инструкции"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Шаг 4: Подтверждение -->
      <div v-if="activeStep === 3" class="step-content">
        <h3>Подтверждение создания испытания</h3>

        <Card>
          <template #content>
            <div class="summary">
              <h4>Информация об испытании</h4>

              <div class="grid">
                <div class="col-6">
                  <p><strong>Материал:</strong></p>
                  <p>{{ selectedMaterial?.material_code }} - {{ selectedMaterial?.name }}</p>
                </div>
                <div class="col-6">
                  <p><strong>Тип испытания:</strong></p>
                  <p>{{ getTestTypeLabel(testForm.test_type) }}</p>
                </div>
                <div class="col-6">
                  <p><strong>Метод:</strong></p>
                  <p>{{ getTestMethodLabel(testForm.test_method) }}</p>
                </div>
                <div class="col-6">
                  <p><strong>Приоритет:</strong></p>
                  <Tag :value="getPriorityLabel(testForm.priority)" :severity="getPrioritySeverity(testForm.priority)" />
                </div>
                <div class="col-6">
                  <p><strong>Ответственный:</strong></p>
                  <p>{{ getAssignedUserName() }}</p>
                </div>
                <div class="col-6">
                  <p><strong>Планируемая дата:</strong></p>
                  <p>{{ formatDate(testForm.scheduled_date) }}</p>
                </div>
                <div v-if="testForm.required_standards?.length" class="col-12">
                  <p><strong>Стандарты:</strong></p>
                  <p>{{ testForm.required_standards.join(', ') }}</p>
                </div>
                <div v-if="testForm.notes" class="col-12">
                  <p><strong>Примечания:</strong></p>
                  <p>{{ testForm.notes }}</p>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <Message severity="info" :closable="false" class="mt-3">
          После создания испытания будет отправлено уведомление ответственному лаборанту.
        </Message>
      </div>
    </div>

    <!-- Кнопки навигации -->
    <div class="flex justify-content-between mt-4">
      <Button
        label="Назад"
        icon="pi pi-arrow-left"
        @click="prevStep"
        :disabled="activeStep === 0"
        severity="secondary"
      />

      <div class="flex gap-2">
        <Button
          label="Отмена"
          severity="secondary"
          @click="handleCancel"
          :disabled="loading"
        />

        <Button
          v-if="activeStep < 3"
          label="Далее"
          icon="pi pi-arrow-right"
          iconPos="right"
          @click="nextStep"
          :disabled="loading"
        />

        <Button
          v-if="activeStep === 3"
          label="Создать испытание"
          icon="pi pi-check"
          @click="handleSubmit"
          :loading="loading"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { testService } from '@/services/testService'
import { materialService } from '@/services/materialService'
import { userService } from '@/services/userService'

const emit = defineEmits(['saved', 'cancel'])

const toast = useToast()
const loading = ref(false)
const activeStep = ref(0)

// Шаги формы
const steps = [
  { label: 'Выбор материала', icon: 'pi pi-box' },
  { label: 'Параметры испытания', icon: 'pi pi-cog' },
  { label: 'Назначение и сроки', icon: 'pi pi-user' },
  { label: 'Подтверждение', icon: 'pi pi-check' }
]

// Данные формы
const testForm = reactive({
  material_id: null,
  test_type: null,
  test_method: null,
  test_category: 'incoming',
  priority: 'normal',
  required_standards: [],
  requirements: '',
  assigned_to: null,
  department: 'ЦЗЛ',
  scheduled_date: null,
  deadline: null,
  equipment: [],
  notes: ''
})

// Выбранный материал
const selectedMaterial = ref(null)
const filteredMaterials = ref([])
const materials = ref([])
const labUsers = ref([])

// Ошибки валидации
const errors = ref({})

// Опции для селектов
const testTypeOptions = [
  { label: 'Механические испытания', value: 'mechanical' },
  { label: 'Химический анализ', value: 'chemical' },
  { label: 'Визуальный контроль', value: 'visual' },
  { label: 'Геометрические измерения', value: 'dimensional' },
  { label: 'Металлография', value: 'metallography' },
  { label: 'Неразрушающий контроль', value: 'non_destructive' }
]

const testCategoryOptions = [
  { label: 'Входной контроль', value: 'incoming' },
  { label: 'Периодический контроль', value: 'periodic' },
  { label: 'Арбитражный контроль', value: 'arbitration' },
  { label: 'Внеплановый контроль', value: 'unscheduled' }
]

const priorityOptions = [
  { label: 'Низкий', value: 'low' },
  { label: 'Обычный', value: 'normal' },
  { label: 'Высокий', value: 'high' },
  { label: 'Срочный', value: 'urgent' }
]

const standardsOptions = [
  { label: 'ГОСТ 1497-84', value: 'ГОСТ 1497-84' },
  { label: 'ГОСТ 9454-78', value: 'ГОСТ 9454-78' },
  { label: 'ГОСТ 9012-59', value: 'ГОСТ 9012-59' },
  { label: 'ГОСТ 22536.0-87', value: 'ГОСТ 22536.0-87' },
  { label: 'ГОСТ 5639-82', value: 'ГОСТ 5639-82' },
  { label: 'ГОСТ 5640-68', value: 'ГОСТ 5640-68' },
  { label: 'ГОСТ 18895-97', value: 'ГОСТ 18895-97' },
  { label: 'ISO 6892-1:2019', value: 'ISO 6892-1:2019' },
  { label: 'ISO 148-1:2016', value: 'ISO 148-1:2016' },
  { label: 'ASTM E8/E8M-21', value: 'ASTM E8/E8M-21' }
]

const equipmentOptions = [
  { label: 'Разрывная машина УТС-110М', value: 'utm_110m' },
  { label: 'Твердомер Бринелля ТБ-5004', value: 'hardness_tb5004' },
  { label: 'Копер маятниковый КМ-30', value: 'impact_km30' },
  { label: 'Спектрометр ARL 3460', value: 'spectrometer_arl3460' },
  { label: 'Микроскоп металлографический МИМ-10', value: 'microscope_mim10' },
  { label: 'Толщиномер ультразвуковой УТ-93П', value: 'thickness_ut93p' },
  { label: 'Дефектоскоп УД2-70', value: 'flaw_detector_ud270' }
]

// Методы испытаний в зависимости от типа
const testMethods = {
  mechanical: [
    { label: 'Растяжение', value: 'tensile' },
    { label: 'Твердость', value: 'hardness' },
    { label: 'Ударная вязкость', value: 'impact' },
    { label: 'Изгиб', value: 'bending' }
  ],
  chemical: [
    { label: 'Спектральный анализ', value: 'spectral' },
    { label: 'Химический анализ', value: 'chemical' },
    { label: 'Газовый анализ', value: 'gas' }
  ],
  visual: [
    { label: 'Визуальный осмотр', value: 'visual' },
    { label: 'Измерительный контроль', value: 'measuring' }
  ],
  dimensional: [
    { label: 'Измерение геометрии', value: 'geometry' },
    { label: 'Контроль плоскостности', value: 'flatness' },
    { label: 'Контроль шероховатости', value: 'roughness' }
  ],
  metallography: [
    { label: 'Макроструктура', value: 'macro' },
    { label: 'Микроструктура', value: 'micro' },
    { label: 'Размер зерна', value: 'grain_size' }
  ],
  non_destructive: [
    { label: 'Ультразвуковой контроль', value: 'ultrasonic' },
    { label: 'Магнитопорошковый контроль', value: 'magnetic' },
    { label: 'Капиллярный контроль', value: 'penetrant' }
  ]
}

// Вспомогательные функции
const getTestMethods = (testType) => {
  return testMethods[testType] || []
}

const getTestTypeLabel = (type) => {
  const option = testTypeOptions.find(opt => opt.value === type)
  return option?.label || type
}

const getTestMethodLabel = (method) => {
  for (const methods of Object.values(testMethods)) {
    const option = methods.find(m => m.value === method)
    if (option) return option.label
  }
  return method
}

const getPriorityLabel = (priority) => {
  const option = priorityOptions.find(opt => opt.value === priority)
  return option?.label || priority
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

const getMaterialStatusSeverity = (status) => {
  const severities = {
    received: 'info',
    quarantine: 'warning',
    testing: 'info',
    approved: 'success',
    rejected: 'danger',
    released: 'success'
  }
  return severities[status] || 'secondary'
}

const getAssignedUserName = () => {
  const user = labUsers.value.find(u => u.id === testForm.assigned_to)
  return user?.full_name || 'Не назначен'
}

const getInitials = (fullName) => {
  if (!fullName) return '?'
  const parts = fullName.split(' ')
  return parts.map(part => part[0]).join('').toUpperCase().slice(0, 2)
}

const getAvatarColor = (userId) => {
  const colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#00BCD4']
  return colors[userId % colors.length]
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

// Поиск материалов
const searchMaterial = async (event) => {
  const query = event.query.toLowerCase()

  if (materials.value.length === 0) {
    await loadMaterials()
  }

  filteredMaterials.value = materials.value
    .filter(m =>
      m.material_code.toLowerCase().includes(query) ||
      m.name.toLowerCase().includes(query) ||
      m.grade?.toLowerCase().includes(query)
    )
    .map(m => ({
      ...m,
      display: `${m.material_code} - ${m.name}`
    }))
    .slice(0, 10)
}

// Загрузка данных
const loadMaterials = async () => {
  try {
    const response = await materialService.getAll({ status: 'quarantine' })
    materials.value = response.items || []
  } catch (error) {
    console.error('Error loading materials:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить список материалов'
    })
  }
}

const loadLabUsers = async () => {
  try {
    labUsers.value = await userService.getLabUsers()
  } catch (error) {
    console.error('Error loading lab users:', error)
    labUsers.value = [
      { id: 1, full_name: 'Иванов И.И.', position: 'Инженер-лаборант' },
      { id: 2, full_name: 'Петров П.П.', position: 'Старший лаборант' },
      { id: 3, full_name: 'Сидорова С.С.', position: 'Техник-лаборант' }
    ]
  }
}

// Валидация шагов
const validateStep = (step) => {
  errors.value = {}
  let isValid = true

  switch (step) {
    case 0:
      if (!selectedMaterial.value || typeof selectedMaterial.value !== 'object') {
        errors.value.material = 'Необходимо выбрать материал'
        isValid = false
      }
      break

    case 1:
      if (!testForm.test_type) {
        errors.value.test_type = 'Необходимо выбрать тип испытания'
        isValid = false
      }
      if (!testForm.test_method) {
        errors.value.test_method = 'Необходимо выбрать метод испытания'
        isValid = false
      }
      break

    case 2:
      if (!testForm.assigned_to) {
        errors.value.assigned_to = 'Необходимо назначить ответственного'
        isValid = false
      }
      if (!testForm.scheduled_date) {
        errors.value.scheduled_date = 'Необходимо указать планируемую дату'
        isValid = false
      }
      break
  }

  return isValid
}

// Навигация по шагам
const nextStep = () => {
  if (validateStep(activeStep.value)) {
    if (activeStep.value === 0 && selectedMaterial.value) {
      testForm.material_id = selectedMaterial.value.id
    }
    activeStep.value++
  }
}

const prevStep = () => {
  activeStep.value--
}

// Обработчики событий
const onTestTypeChange = () => {
  testForm.test_method = null
}

// Отправка формы
const handleSubmit = async () => {
  loading.value = true

  try {
    const response = await testService.create({
      ...testForm,
      material_id: selectedMaterial.value.id
    })

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Испытание №${response.test_id} успешно создано`
    })

    emit('saved', response)

  } catch (error) {
    console.error('Error creating test:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось создать испытание'
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

// Загрузка данных при монтировании
onMounted(() => {
  loadLabUsers()
})
</script>

<style scoped>
.new-test-form {
  padding: 1rem;
}

.step-content {
  min-height: 400px;
}

.step-content h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.required::after {
  content: " *";
  color: var(--red-500);
}

.material-option {
  padding: 0.25rem 0;
}

.summary h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.summary p {
  margin: 0.5rem 0;
}

.summary p strong {
  color: var(--text-color-secondary);
}

.text-secondary {
  color: var(--text-color-secondary);
}

.w-full {
  width: 100%;
}
</style>