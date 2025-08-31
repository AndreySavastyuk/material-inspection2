<template>
  <Dialog
    :visible="props.visible"
    @update:visible="emit('update:visible', $event)"
    modal
    header="Добавление результатов испытания"
    :style="{ width: '900px' }"
    :draggable="false"
  >
    <div v-if="test">
      <!-- Информация об испытании -->
      <div class="test-info">
        <h3>Информация об испытании</h3>
        <div class="grid">
          <div class="col-6">
            <strong>Материал:</strong> {{ test.material?.name || 'N/A' }}
          </div>
          <div class="col-6">
            <strong>Тип испытания:</strong> {{ getTestTypeLabel(test.test_type) }}
          </div>
          <div class="col-6">
            <strong>Метод:</strong> {{ getTestMethodLabel(test.test_method) }}
          </div>
          <div class="col-6">
            <strong>Статус:</strong>
            <Tag :value="test.status" :severity="getStatusSeverity(test.status)" />
          </div>
        </div>
      </div>

      <Divider />

      <!-- Форма результатов -->
      <form @submit.prevent="handleSubmit">
        <div class="grid">
          <!-- Основные результаты -->
          <div class="col-12">
            <h3>Результаты испытания</h3>
          </div>

          <!-- Механические испытания -->
          <template v-if="test.test_type === 'mechanical'">
            <div class="col-4">
              <div class="field">
                <label for="tensileStrength">Предел прочности, МПа</label>
                <InputNumber
                  id="tensileStrength"
                  v-model="results.tensile_strength"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="yieldStrength">Предел текучести, МПа</label>
                <InputNumber
                  id="yieldStrength"
                  v-model="results.yield_strength"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="elongation">Относительное удлинение, %</label>
                <InputNumber
                  id="elongation"
                  v-model="results.elongation"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="hardness">Твердость, HB</label>
                <InputNumber
                  id="hardness"
                  v-model="results.hardness"
                  :minFractionDigits="0"
                  :maxFractionDigits="0"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="impactStrength">Ударная вязкость, Дж/см²</label>
                <InputNumber
                  id="impactStrength"
                  v-model="results.impact_strength"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>
          </template>

          <!-- Химический анализ -->
          <template v-if="test.test_type === 'chemical'">
            <div class="col-12">
              <h4>Химический состав, %</h4>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="carbon">Углерод (C)</label>
                <InputNumber
                  id="carbon"
                  v-model="results.chemical_composition.C"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="silicon">Кремний (Si)</label>
                <InputNumber
                  id="silicon"
                  v-model="results.chemical_composition.Si"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="manganese">Марганец (Mn)</label>
                <InputNumber
                  id="manganese"
                  v-model="results.chemical_composition.Mn"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="phosphorus">Фосфор (P)</label>
                <InputNumber
                  id="phosphorus"
                  v-model="results.chemical_composition.P"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="sulfur">Сера (S)</label>
                <InputNumber
                  id="sulfur"
                  v-model="results.chemical_composition.S"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="chromium">Хром (Cr)</label>
                <InputNumber
                  id="chromium"
                  v-model="results.chemical_composition.Cr"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="nickel">Никель (Ni)</label>
                <InputNumber
                  id="nickel"
                  v-model="results.chemical_composition.Ni"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
            <div class="col-3">
              <div class="field">
                <label for="copper">Медь (Cu)</label>
                <InputNumber
                  id="copper"
                  v-model="results.chemical_composition.Cu"
                  :minFractionDigits="3"
                  :maxFractionDigits="3"
                />
              </div>
            </div>
          </template>

          <!-- Визуальный контроль -->
          <template v-if="test.test_type === 'visual'">
            <div class="col-6">
              <div class="field">
                <label for="surface_quality">Качество поверхности</label>
                <Dropdown
                  id="surface_quality"
                  v-model="results.surface_quality"
                  :options="surfaceQualityOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Выберите"
                />
              </div>
            </div>

            <div class="col-6">
              <div class="field">
                <label for="defects_found">Обнаружены дефекты</label>
                <SelectButton
                  v-model="results.defects_found"
                  :options="[
                    { label: 'Да', value: 'true' },
                    { label: 'Нет', value: 'false' }
                  ]"
                  optionLabel="label"
                  optionValue="value"
                />
              </div>
            </div>

            <div v-if="results.defects_found === 'true'" class="col-12">
              <div class="field">
                <label for="defect_description">Описание дефектов</label>
                <Textarea
                  id="defect_description"
                  v-model="results.defect_description"
                  rows="3"
                  :class="{ 'p-invalid': errors.defect_description }"
                />
                <small v-if="errors.defect_description" class="p-error">
                  {{ errors.defect_description }}
                </small>
              </div>
            </div>

            <div v-if="results.defects_found === 'true'" class="col-6">
              <div class="field">
                <label for="defect_type">Тип дефекта</label>
                <MultiSelect
                  id="defect_type"
                  v-model="results.defect_types"
                  :options="defectTypeOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Выберите типы дефектов"
                />
              </div>
            </div>

            <div v-if="results.defects_found === 'true'" class="col-6">
              <div class="field">
                <label for="defect_count">Количество дефектов</label>
                <InputNumber
                  id="defect_count"
                  v-model="results.defect_count"
                  :min="1"
                />
              </div>
            </div>
          </template>

          <!-- Геометрические измерения -->
          <template v-if="test.test_type === 'dimensional'">
            <div class="col-4">
              <div class="field">
                <label for="thickness">Толщина, мм <span class="required"></span></label>
                <InputNumber
                  id="thickness"
                  v-model="results.thickness"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :class="{ 'p-invalid': errors.thickness }"
                />
                <small v-if="errors.thickness" class="p-error">{{ errors.thickness }}</small>
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="width">Ширина, мм</label>
                <InputNumber
                  id="width"
                  v-model="results.width"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="length">Длина, мм</label>
                <InputNumber
                  id="length"
                  v-model="results.length"
                  :minFractionDigits="1"
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-6">
              <div class="field">
                <label for="flatness">Плоскостность, мм</label>
                <InputNumber
                  id="flatness"
                  v-model="results.flatness"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                />
              </div>
            </div>

            <div class="col-6">
              <div class="field">
                <label for="roughness">Шероховатость, Ra</label>
                <InputNumber
                  id="roughness"
                  v-model="results.roughness"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                />
              </div>
            </div>
          </template>

          <!-- Общие поля для всех типов испытаний -->
          <div class="col-12">
            <Divider />
            <h3>Заключение</h3>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="test_result">Результат испытания <span class="required"></span></label>
              <SelectButton
                v-model="results.pass_fail"
                :options="[
                  { label: 'Соответствует', value: 'PASS', severity: 'success' },
                  { label: 'Не соответствует', value: 'FAIL', severity: 'danger' }
                ]"
                optionLabel="label"
                optionValue="value"
                :class="{ 'p-invalid': errors.pass_fail }"
              />
              <small v-if="errors.pass_fail" class="p-error">{{ errors.pass_fail }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="test_date">Дата испытания <span class="required"></span></label>
              <Calendar
                id="test_date"
                v-model="results.test_date"
                dateFormat="dd.mm.yy"
                showIcon
                :class="{ 'p-invalid': errors.test_date }"
              />
              <small v-if="errors.test_date" class="p-error">{{ errors.test_date }}</small>
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="notes">Примечания</label>
              <Textarea
                id="notes"
                v-model="results.notes"
                rows="3"
                placeholder="Дополнительные комментарии к результатам испытания"
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="attachments">Приложения</label>
              <FileUpload
                ref="fileUpload"
                name="attachments"
                :multiple="true"
                accept="image/*,application/pdf"
                :maxFileSize="10000000"
                @upload="onUpload"
                @error="onUploadError"
                :auto="false"
                chooseLabel="Выбрать файлы"
                uploadLabel="Загрузить"
                cancelLabel="Отмена"
              >
                <template #empty>
                  <p>Перетащите файлы сюда или нажмите для выбора</p>
                </template>
              </FileUpload>
            </div>
          </div>
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
            label="Сохранить результаты"
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
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { testService } from '@/services/testService'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  test: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'saved', 'cancel'])

const toast = useToast()
const loading = ref(false)
const fileUpload = ref(null)

// Форма результатов
const results = reactive({
  // Механические испытания
  tensile_strength: null,
  yield_strength: null,
  elongation: null,
  hardness: null,
  impact_strength: null,

  // Химический состав
  chemical_composition: {
    C: null,
    Si: null,
    Mn: null,
    P: null,
    S: null,
    Cr: null,
    Ni: null,
    Cu: null
  },

  // Визуальный контроль
  surface_quality: null,
  defects_found: 'false',
  defect_description: '',
  defect_types: [],
  defect_count: 0,

  // Геометрические измерения
  thickness: null,
  width: null,
  length: null,
  flatness: null,
  roughness: null,

  // Общие поля
  pass_fail: null,
  test_date: new Date(),
  notes: '',
  attachments: []
})

// Ошибки валидации
const errors = ref({})

// Опции для селектов
const surfaceQualityOptions = [
  { label: 'Отличное', value: 'excellent' },
  { label: 'Хорошее', value: 'good' },
  { label: 'Удовлетворительное', value: 'satisfactory' },
  { label: 'Неудовлетворительное', value: 'unsatisfactory' }
]

const defectTypeOptions = [
  { label: 'Царапины', value: 'scratches' },
  { label: 'Вмятины', value: 'dents' },
  { label: 'Коррозия', value: 'corrosion' },
  { label: 'Трещины', value: 'cracks' },
  { label: 'Раковины', value: 'cavities' },
  { label: 'Включения', value: 'inclusions' },
  { label: 'Расслоение', value: 'delamination' },
  { label: 'Прочие', value: 'other' }
]

// Вспомогательные функции
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
    measuring: 'Измерение'
  }
  return labels[method] || method
}

const getStatusSeverity = (status) => {
  const severities = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    failed: 'danger'
  }
  return severities[status] || 'secondary'
}

// Валидация формы
const validateForm = () => {
  errors.value = {}
  let isValid = true

  // Обязательные поля
  if (!results.pass_fail) {
    errors.value.pass_fail = 'Необходимо указать результат испытания'
    isValid = false
  }

  if (!results.test_date) {
    errors.value.test_date = 'Необходимо указать дату испытания'
    isValid = false
  }

  // Валидация по типу испытания
  if (props.test?.test_type === 'dimensional' && !results.thickness) {
    errors.value.thickness = 'Толщина обязательна для измерения'
    isValid = false
  }

  if (props.test?.test_type === 'visual' && results.defects_found === 'true' && !results.defect_description) {
    errors.value.defect_description = 'Необходимо описать обнаруженные дефекты'
    isValid = false
  }

  return isValid
}

// Обработка загрузки файлов
const onUpload = (event) => {
  results.attachments = [...results.attachments, ...event.files]
  toast.add({
    severity: 'success',
    summary: 'Успешно',
    detail: `Загружено файлов: ${event.files.length}`
  })
}

const onUploadError = (error) => {
  toast.add({
    severity: 'error',
    summary: 'Ошибка загрузки',
    detail: 'Не удалось загрузить файл'
  })
}

// Отправка формы
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const resultData = {
      test_id: props.test.id,
      ...results,
      status: 'completed'
    }

    await testService.addResults(props.test.id, resultData)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Результаты испытания сохранены'
    })

    emit('saved', resultData)
    handleCancel()

  } catch (error) {
    console.error('Error saving test results:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось сохранить результаты'
    })
  } finally {
    loading.value = false
  }
}

// Отмена
const handleCancel = () => {
  // Сброс формы
  Object.keys(results).forEach(key => {
    if (key === 'chemical_composition') {
      Object.keys(results[key]).forEach(element => {
        results[key][element] = null
      })
    } else if (key === 'defects_found') {
      results[key] = 'false'
    } else if (key === 'defect_count') {
      results[key] = 0
    } else if (key === 'test_date') {
      results[key] = new Date()
    } else if (key === 'attachments') {
      results[key] = []
    } else if (typeof results[key] === 'string') {
      results[key] = ''
    } else {
      results[key] = null
    }
  })
  
  errors.value = {}
  emit('update:visible', false)
  emit('cancel')
}
</script>

<style scoped>
.test-info {
  background: var(--surface-100);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}

.test-info h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--primary-color);
}

.field {
  margin-bottom: 1rem;
}

.required::after {
  content: " *";
  color: var(--red-500);
}

h3, h4 {
  margin: 1rem 0 0.5rem 0;
  color: var(--primary-color);
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.grid .col-12:first-child h3 {
  margin-top: 0;
}
</style>