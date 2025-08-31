<template>
  <Dialog :visible="props.visible" @update:visible="emit('update:visible', $event)" modal header="Добавление результатов испытания" :style="{ width: '900px' }" :draggable="false">
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
                  :maxFractionDigits="2"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="reductionOfArea">Относительное сужение, %</label>
                <InputNumber
                  id="reductionOfArea"
                  v-model="results.reduction_of_area"
                  :minFractionDigits="1"
                  :maxFractionDigits="2"
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
                  :maxFractionDigits="1"
                />
              </div>
            </div>

            <div class="col-4">
              <div class="field">
                <label for="impactEnergy">Ударная вязкость, Дж</label>
                <InputNumber
                  id="impactEnergy"
                  v-model="results.impact_energy"
                  :minFractionDigits="0"
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
            
            <div class="col-3" v-for="element in chemicalElements" :key="element.symbol">
              <div class="field">
                <label :for="element.symbol">{{ element.name }} ({{ element.symbol }})</label>
                <InputNumber
                  :id="element.symbol"
                  v-model="results.chemical_composition[element.symbol]"
                  :minFractionDigits="2"
                  :maxFractionDigits="4"
                  :min="0"
                  :max="100"
                />
              </div>
            </div>
          </template>

          <!-- Неразрушающий контроль -->
          <template v-if="test.test_type === 'non_destructive'">
            <div class="col-6">
              <div class="field">
                <label for="defectsFound">Дефекты обнаружены</label>
                <div class="flex align-items-center gap-2 mt-2">
                  <RadioButton 
                    id="defects_yes" 
                    name="defectsFound" 
                    value="true" 
                    v-model="results.defects_found" 
                  />
                  <label for="defects_yes">Да</label>
                  <RadioButton 
                    id="defects_no" 
                    name="defectsFound" 
                    value="false" 
                    v-model="results.defects_found" 
                  />
                  <label for="defects_no">Нет</label>
                </div>
              </div>
            </div>

            <div class="col-6" v-if="results.defects_found === 'true'">
              <div class="field">
                <label for="defectCount">Количество дефектов</label>
                <InputNumber
                  id="defectCount"
                  v-model="results.defect_count"
                  :min="0"
                />
              </div>
            </div>

            <div class="col-12" v-if="results.defects_found === 'true'">
              <div class="field">
                <label for="defectDescription">Описание дефектов</label>
                <Textarea
                  id="defectDescription"
                  v-model="results.defect_description"
                  rows="3"
                  placeholder="Опишите обнаруженные дефекты"
                />
              </div>
            </div>
          </template>

          <!-- Общие поля -->
          <div class="col-12">
            <h3>Заключение</h3>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="conclusion" class="required">Заключение</label>
              <Dropdown
                id="conclusion"
                v-model="results.conclusion"
                :options="conclusions"
                optionLabel="label"
                optionValue="value"
                placeholder="Выберите заключение"
                :class="{ 'p-invalid': errors.conclusion }"
                required
              />
              <small class="p-error" v-if="errors.conclusion">{{ errors.conclusion }}</small>
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="testDate">Дата проведения испытания</label>
              <Calendar
                id="testDate"
                v-model="results.test_date"
                dateFormat="dd.mm.yy"
                placeholder="Выберите дату"
              />
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="operator">Испытал</label>
              <InputText
                id="operator"
                v-model="results.operator"
                placeholder="ФИО оператора"
              />
            </div>
          </div>

          <div class="col-6">
            <div class="field">
              <label for="equipment">Оборудование</label>
              <InputText
                id="equipment"
                v-model="results.equipment"
                placeholder="Использованное оборудование"
              />
            </div>
          </div>

          <div class="col-12">
            <div class="field">
              <label for="notes">Примечания</label>
              <Textarea
                id="notes"
                v-model="results.notes"
                rows="3"
                placeholder="Дополнительные замечания"
              />
            </div>
          </div>

          <!-- Загрузка фотографий -->
          <div class="col-12">
            <h3>Фотографии и документы</h3>
          </div>

          <div class="col-12">
            <FileUpload
              name="files"
              :multiple="true"
              accept="image/*,.pdf"
              :maxFileSize="5000000"
              @upload="onFilesUpload"
              @error="onUploadError"
              :auto="false"
              chooseLabel="Выбрать файлы"
              uploadLabel="Загрузить"
              cancelLabel="Отмена"
            >
              <template #content="{ files, uploadedFiles, removeUploadedFileCallback, removeFileCallback }">
                <div v-if="files.length > 0">
                  <div class="flex flex-wrap gap-2">
                    <div v-for="(file, index) in files" :key="file.name + file.type + file.size" class="card m-0 px-2 py-1">
                      <span class="text-sm">{{ file.name }}</span>
                      <Button 
                        icon="pi pi-times" 
                        @click="removeFileCallback(index)" 
                        severity="danger"
                        text
                        rounded
                        size="small"
                      />
                    </div>
                  </div>
                </div>
              </template>
            </FileUpload>
          </div>
        </div>
      </form>
    </div>

    <template #footer>
      <Button 
        label="Отмена" 
        severity="secondary" 
        @click="handleCancel"
        :disabled="loading"
      />
      <Button 
        label="Сохранить результаты" 
        @click="handleSubmit"
        :loading="loading"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import FileUpload from 'primevue/fileupload'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
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
const errors = ref({})

// Результаты испытания
const results = reactive({
  // Механические свойства
  tensile_strength: null,
  yield_strength: null,
  elongation: null,
  reduction_of_area: null,
  hardness: null,
  impact_energy: null,
  
  // Химический состав
  chemical_composition: {},
  
  // НК
  defects_found: 'false',
  defect_count: 0,
  defect_description: '',
  
  // Общие поля
  conclusion: null,
  test_date: new Date(),
  operator: '',
  equipment: '',
  notes: '',
  
  // Файлы
  attachments: []
})

// Заключения
const conclusions = [
  { label: 'Годен', value: 'accepted' },
  { label: 'Годен с ограничениями', value: 'accepted_with_limitations' },
  { label: 'Не годен', value: 'rejected' },
  { label: 'Требует дополнительных исследований', value: 'needs_additional_testing' }
]

// Химические элементы
const chemicalElements = [
  { symbol: 'C', name: 'Углерод' },
  { symbol: 'Si', name: 'Кремний' },
  { symbol: 'Mn', name: 'Марганец' },
  { symbol: 'P', name: 'Фосфор' },
  { symbol: 'S', name: 'Сера' },
  { symbol: 'Cr', name: 'Хром' },
  { symbol: 'Ni', name: 'Никель' },
  { symbol: 'Mo', name: 'Молибден' },
  { symbol: 'V', name: 'Ванадий' },
  { symbol: 'Ti', name: 'Титан' },
  { symbol: 'Al', name: 'Алюминий' },
  { symbol: 'Cu', name: 'Медь' }
]

// Инициализация химического состава
onMounted(() => {
  chemicalElements.forEach(element => {
    results.chemical_composition[element.symbol] = null
  })
})

// Получение названия типа испытания
const getTestTypeLabel = (type) => {
  const types = {
    'mechanical': 'Механические испытания',
    'chemical': 'Химический анализ',
    'non_destructive': 'Неразрушающий контроль',
    'metallographic': 'Металлографические исследования',
    'corrosion': 'Коррозионная стойкость'
  }
  return types[type] || type
}

// Получение названия метода испытания
const getTestMethodLabel = (method) => {
  const methods = {
    'tensile': 'Растяжение',
    'bend': 'Изгиб',
    'impact': 'Удар',
    'hardness': 'Твердость',
    'spectral': 'Спектральный анализ',
    'wet_chemistry': 'Химический анализ',
    'xrf': 'Рентгенофлуоресцентный',
    'ultrasonic': 'УЗК',
    'magnetic_particle': 'МПК',
    'visual': 'ВИК',
    'radiographic': 'Рентгеновский'
  }
  return methods[method] || method
}

// Получение цвета для статуса
const getStatusSeverity = (status) => {
  const severities = {
    'planned': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'cancelled': 'danger'
  }
  return severities[status] || 'info'
}

// Валидация формы
const validateForm = () => {
  errors.value = {}

  if (!results.conclusion) {
    errors.value.conclusion = 'Выберите заключение'
  }

  return Object.keys(errors.value).length === 0
}

// Загрузка файлов
const onFilesUpload = (event) => {
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