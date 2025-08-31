<template>
  <div class="edit-test-form">
    <div v-if="test">
      <!-- Информация о материале -->
      <Card class="mb-3">
        <template #title>Информация о материале</template>
        <template #content>
          <div class="grid">
            <div class="col-4">
              <p><strong>Код:</strong> {{ test.material?.material_code }}</p>
            </div>
            <div class="col-4">
              <p><strong>Название:</strong> {{ test.material?.name }}</p>
            </div>
            <div class="col-4">
              <p><strong>Марка:</strong> {{ test.material?.grade }}</p>
            </div>
          </div>
        </template>
      </Card>

      <!-- Форма редактирования -->
      <form @submit.prevent="handleSubmit">
        <div class="grid">
          <!-- Параметры испытания -->
          <div class="col-12">
            <h3>Параметры испытания</h3>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="test_type">Тип испытания <span class="required"></span></label>
              <Dropdown
                id="test_type"
                v-model="formData.test_type"
                :options="testTypeOptions"
                optionLabel="label"
                optionValue="value"
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
                v-model="formData.test_method"
                :options="getTestMethods(formData.test_type)"
                optionLabel="label"
                optionValue="value"
                :disabled="!formData.test_type"
                :class="{ 'p-invalid': errors.test_method }"
              />
              <small v-if="errors.test_method" class="p-error">{{ errors.test_method }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="status">Статус испытания</label>
              <Dropdown
                id="status"
                v-model="formData.status"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
              />
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="priority">Приоритет</label>
              <SelectButton
                v-model="formData.priority"
                :options="priorityOptions"
                optionLabel="label"
                optionValue="value"
              />
            </div>
          </div>

          <!-- Результаты испытания (если есть) -->
          <template v-if="formData.status === 'completed' && formData.results">
            <div class="col-12">
              <Divider />
              <h3>Результаты испытания</h3>
            </div>

            <div class="col-6">
              <div class="field">
                <label for="pass_fail">Результат</label>
                <SelectButton
                  v-model="formData.results.pass_fail"
                  :options="[
                    { label: 'Соответствует', value: 'PASS' },
                    { label: 'Не соответствует', value: 'FAIL' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                />
              </div>
            </div>

            <div class="col-6">
              <div class="field">
                <label for="test_date">Дата проведения</label>
                <Calendar
                  id="test_date"
                  v-model="formData.results.test_date"
                  dateFormat="dd.mm.yy"
                  showIcon
                />
              </div>
            </div>

            <!-- Результаты по типу испытания -->
            <template v-if="formData.test_type === 'mechanical'">
              <div class="col-3">
                <div class="field">
                  <label>Предел прочности, МПа</label>
                  <InputNumber
                    v-model="formData.results.tensile_strength"
                    :minFractionDigits="1"
                    :maxFractionDigits="1"
                  />
                </div>
              </div>
              <div class="col-3">
                <div class="field">
                  <label>Предел текучести, МПа</label>
                  <InputNumber
                    v-model="formData.results.yield_strength"
                    :minFractionDigits="1"
                    :maxFractionDigits="1"
                  />
                </div>
              </div>
              <div class="col-3">
                <div class="field">
                  <label>Относительное удлинение, %</label>
                  <InputNumber
                    v-model="formData.results.elongation"
                    :minFractionDigits="1"
                    :maxFractionDigits="1"
                  />
                </div>
              </div>
              <div class="col-3">
                <div class="field">
                  <label>Твердость, HB</label>
                  <InputNumber
                    v-model="formData.results.hardness"
                    :minFractionDigits="0"
                    :maxFractionDigits="0"
                  />
                </div>
              </div>
            </template>

            <div class="col-12">
              <div class="field">
                <label for="result_notes">Примечания к результатам</label>
                <Textarea
                  id="result_notes"
                  v-model="formData.results.notes"
                  rows="3"
                />
              </div>
            </div>
          </template>

          <!-- Назначение и сроки -->
          <div class="col-12">
            <Divider />
            <h3>Назначение и сроки</h3>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="assigned_to">Ответственный лаборант <span class="required"></span></label>
              <Dropdown
                id="assigned_to"
                v-model="formData.assigned_to"
                :options="labUsers"
                optionLabel="full_name"
                optionValue="id"
                :class="{ 'p-invalid': errors.assigned_to }"
                filter
              >
                <template #option="slotProps">
                  <div class="flex align-items-center">
                    <Avatar
                      :label="getInitials(slotProps.option.full_name)"
                      class="mr-2"
                      size="small"
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
              <label for="scheduled_date">Планируемая дата <span class="required"></span></label>
              <Calendar
                id="scheduled_date"
                v-model="formData.scheduled_date"
                dateFormat="dd.mm.yy"
                showIcon
                :class="{ 'p-invalid': errors.scheduled_date }"
              />
              <small v-if="errors.scheduled_date" class="p-error">{{ errors.scheduled_date }}</small>
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="standards">Стандарты испытаний</label>
              <MultiSelect
                id="standards"
                v-model="formData.required_standards"
                :options="standardsOptions"
                optionLabel="label"
                optionValue="value"
                display="chip"
                filter
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="notes">Примечания</label>
              <Textarea
                id="notes"
                v-model="formData.notes"
                rows="3"
              />
            </div>
          </div>
        </div>

        <!-- История изменений -->
        <div v-if="changeHistory.length > 0" class="mt-4">
          <Divider />
          <h3>История изменений</h3>
          <Timeline :value="changeHistory">
            <template #content="slotProps">
              <div class="timeline-content">
                <div class="timeline-header">
                  <strong>{{ slotProps.item.user }}</strong>
                  <span class="text-secondary ml-2">{{ formatDateTime(slotProps.item.date) }}</span>
                </div>
                <div class="timeline-body">
                  {{ slotProps.item.description }}
                </div>
              </div>
            </template>
          </Timeline>
        </div>

        <!-- Кнопки действий -->
        <div class="flex justify-content-end gap-2 mt-4">
          <Button
            label="Отмена"
            severity="secondary"
            @click="handleCancel"
            :disabled="loading"
          />
          <Button
            label="Сохранить изменения"
            icon="pi pi-check"
            @click="handleSubmit"
            :loading="loading"
          />
        </div>
      </form>
    </div>

    <div v-else class="p-4">
      <Message severity="warn" :closable="false">
        Испытание не выбрано
      </Message>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { testService } from '@/services/testService'
import { userService } from '@/services/userService'

const props = defineProps({
  test: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['saved', 'cancel'])

const toast = useToast()
const loading = ref(false)

// Данные формы
const formData = reactive({
  test_type: null,
  test_method: null,
  status: null,
  priority: null,
  assigned_to: null,
  scheduled_date: null,
  required_standards: [],
  notes: '',
  results: {
    pass_fail: null,
    test_date: null,
    tensile_strength: null,
    yield_strength: null,
    elongation: null,
    hardness: null,
    notes: ''
  }
})

// Дополнительные данные
const labUsers = ref([])
const changeHistory = ref([])
const errors = ref({})

// Опции для селектов
const testTypeOptions = [
  { label: 'Механические испытания', value: 'mechanical' },
  { label: 'Химический анализ', value: 'chemical' },
  { label: 'Визуальный контроль', value: 'visual' },
  { label: 'Геометрические измерения', value: 'dimensional' },
  { label: 'Металлография', value: 'metallography' }
]

const statusOptions = [
  { label: 'Ожидает', value: 'pending' },
  { label: 'В процессе', value: 'in_progress' },
  { label: 'Завершено', value: 'completed' },
  { label: 'Отменено', value: 'cancelled' }
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
  { label: 'ГОСТ 5639-82', value: 'ГОСТ 5639-82' }
]

const testMethods = {
  mechanical: [
    { label: 'Растяжение', value: 'tensile' },
    { label: 'Твердость', value: 'hardness' },
    { label: 'Ударная вязкость', value: 'impact' }
  ],
  chemical: [
    { label: 'Спектральный анализ', value: 'spectral' },
    { label: 'Химический анализ', value: 'chemical' }
  ],
  visual: [
    { label: 'Визуальный осмотр', value: 'visual' }
  ],
  dimensional: [
    { label: 'Измерение геометрии', value: 'geometry' }
  ],
  metallography: [
    { label: 'Микроструктура', value: 'micro' }
  ]
}

// Вспомогательные функции
const getTestMethods = (testType) => {
  return testMethods[testType] || []
}

const getInitials = (fullName) => {
  if (!fullName) return '?'
  const parts = fullName.split(' ')
  return parts.map(part => part[0]).join('').toUpperCase().slice(0, 2)
}

const formatDateTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('ru-RU')
}

// Инициализация данных формы
const initFormData = () => {
  if (!props.test) return

  formData.test_type = props.test.test_type
  formData.test_method = props.test.test_method
  formData.status = props.test.status
  formData.priority = props.test.priority || 'normal'
  formData.assigned_to = props.test.assigned_to
  formData.scheduled_date = props.test.scheduled_date ? new Date(props.test.scheduled_date) : null
  formData.required_standards = props.test.required_standards || []
  formData.notes = props.test.notes || ''

  if (props.test.results) {
    formData.results = { ...props.test.results }
    if (formData.results.test_date) {
      formData.results.test_date = new Date(formData.results.test_date)
    }
  }
}

// Загрузка данных
const loadLabUsers = async () => {
  try {
    labUsers.value = await userService.getLabUsers()
  } catch (error) {
    console.error('Error loading lab users:', error)
    labUsers.value = [
      { id: 1, full_name: 'Иванов И.И.', position: 'Инженер-лаборант' },
      { id: 2, full_name: 'Петров П.П.', position: 'Старший лаборант' }
    ]
  }
}

const loadChangeHistory = () => {
  // Загрузка истории изменений (заглушка)
  changeHistory.value = [
    {
      date: new Date(),
      user: 'Иванов И.И.',
      description: 'Создано испытание'
    }
  ]
}

// Валидация формы
const validateForm = () => {
  errors.value = {}
  let isValid = true

  if (!formData.test_type) {
    errors.value.test_type = 'Необходимо выбрать тип испытания'
    isValid = false
  }

  if (!formData.test_method) {
    errors.value.test_method = 'Необходимо выбрать метод испытания'
    isValid = false
  }

  if (!formData.assigned_to) {
    errors.value.assigned_to = 'Необходимо назначить ответственного'
    isValid = false
  }

  if (!formData.scheduled_date) {
    errors.value.scheduled_date = 'Необходимо указать планируемую дату'
    isValid = false
  }

  return isValid
}

// Обработчики событий
const onTestTypeChange = () => {
  formData.test_method = null
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const updateData = {
      ...formData,
      id: props.test.id
    }

    await testService.update(props.test.id, updateData)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Испытание успешно обновлено'
    })

    emit('saved', updateData)

  } catch (error) {
    console.error('Error updating test:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось обновить испытание'
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
}

// Следим за изменениями пропса test
watch(() => props.test, () => {
  initFormData()
}, { immediate: true })

// Загрузка данных при монтировании
onMounted(() => {
  loadLabUsers()
  loadChangeHistory()
})
</script>

<style scoped>
.edit-test-form {
  padding: 1rem;
}

h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--primary-color);
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
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

.timeline-content {
  padding: 0.5rem 0;
}

.timeline-header {
  margin-bottom: 0.25rem;
}

.timeline-body {
  color: var(--text-color-secondary);
}

.text-secondary {
  color: var(--text-color-secondary);
}