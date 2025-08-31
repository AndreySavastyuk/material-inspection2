<template>
  <Dialog :visible="props.visible" @update:visible="emit('update:visible', $event)" modal header="Создание нового испытания" :style="{ width: '800px' }" :draggable="false">
    <form @submit.prevent="handleSubmit">
      <div class="grid">
        <!-- Основная информация -->
        <div class="col-12">
          <h3>Основная информация</h3>
        </div>
        
        <div class="col-6">
          <div class="field">
            <label for="material" class="required">Материал</label>
            <Dropdown
              id="material"
              v-model="form.materialId"
              :options="materials"
              optionLabel="name"
              optionValue="id"
              placeholder="Выберите материал"
              :class="{ 'p-invalid': errors.materialId }"
              required
            />
            <small class="p-error" v-if="errors.materialId">{{ errors.materialId }}</small>
          </div>
        </div>

        <div class="col-6">
          <div class="field">
            <label for="testType" class="required">Тип испытания</label>
            <Dropdown
              id="testType"
              v-model="form.testType"
              :options="testTypes"
              optionLabel="label"
              optionValue="value"
              placeholder="Выберите тип испытания"
              :class="{ 'p-invalid': errors.testType }"
              required
            />
            <small class="p-error" v-if="errors.testType">{{ errors.testType }}</small>
          </div>
        </div>

        <div class="col-6">
          <div class="field">
            <label for="testMethod">Метод испытания</label>
            <Dropdown
              id="testMethod"
              v-model="form.testMethod"
              :options="availableMethods"
              optionLabel="label"
              optionValue="value"
              placeholder="Выберите метод"
              :disabled="!form.testType"
            />
          </div>
        </div>

        <div class="col-6">
          <div class="field">
            <label for="priority">Приоритет</label>
            <Dropdown
              id="priority"
              v-model="form.priority"
              :options="priorities"
              optionLabel="label"
              optionValue="value"
              placeholder="Выберите приоритет"
            />
          </div>
        </div>

        <!-- Параметры испытания -->
        <div class="col-12">
          <h3>Параметры испытания</h3>
        </div>

        <div class="col-6">
          <div class="field">
            <label for="temperature">Температура, °C</label>
            <InputNumber
              id="temperature"
              v-model="form.temperature"
              :minFractionDigits="0"
              :maxFractionDigits="1"
            />
          </div>
        </div>

        <div class="col-6">
          <div class="field">
            <label for="sampleCount">Количество образцов</label>
            <InputNumber
              id="sampleCount"
              v-model="form.sampleCount"
              :min="1"
              :max="20"
            />
          </div>
        </div>

        <div class="col-12">
          <div class="field">
            <label for="requirements">Требования к испытанию</label>
            <Textarea
              id="requirements"
              v-model="form.requirements"
              rows="3"
              placeholder="Укажите специальные требования или стандарты"
            />
          </div>
        </div>

        <!-- Ожидаемые результаты -->
        <div class="col-12" v-if="form.testType">
          <h3>Ожидаемые результаты</h3>
        </div>

        <div class="col-6" v-if="form.testType === 'mechanical'">
          <div class="field">
            <label for="expectedStrength">Ожидаемая прочность, МПа</label>
            <InputNumber
              id="expectedStrength"
              v-model="form.expectedStrength"
              :minFractionDigits="0"
              :maxFractionDigits="1"
            />
          </div>
        </div>

        <div class="col-6" v-if="form.testType === 'mechanical'">
          <div class="field">
            <label for="expectedElongation">Ожидаемое удлинение, %</label>
            <InputNumber
              id="expectedElongation"
              v-model="form.expectedElongation"
              :minFractionDigits="0"
              :maxFractionDigits="2"
            />
          </div>
        </div>

        <div class="col-12">
          <div class="field">
            <label for="notes">Примечания</label>
            <Textarea
              id="notes"
              v-model="form.notes"
              rows="2"
              placeholder="Дополнительные заметки"
            />
          </div>
        </div>
      </div>
    </form>

    <template #footer>
      <Button 
        label="Отмена" 
        severity="secondary" 
        @click="handleCancel"
        :disabled="loading"
      />
      <Button 
        label="Создать испытание" 
        @click="handleSubmit"
        :loading="loading"
      />
    </template>
  </Dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import { testService } from '@/services/testService'
import { materialService } from '@/services/materialService'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  materialId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'saved', 'cancel'])

const toast = useToast()
const loading = ref(false)
const materials = ref([])

// Форма
const form = reactive({
  materialId: props.materialId || null,
  testType: null,
  testMethod: null,
  priority: 'medium',
  temperature: 20,
  sampleCount: 3,
  requirements: '',
  expectedStrength: null,
  expectedElongation: null,
  notes: ''
})

// Ошибки валидации
const errors = ref({})

// Типы испытаний
const testTypes = [
  { label: 'Механические испытания', value: 'mechanical' },
  { label: 'Химический анализ', value: 'chemical' },
  { label: 'Неразрушающий контроль', value: 'non_destructive' },
  { label: 'Металлографические исследования', value: 'metallographic' },
  { label: 'Коррозионная стойкость', value: 'corrosion' }
]

// Приоритеты
const priorities = [
  { label: 'Низкий', value: 'low' },
  { label: 'Средний', value: 'medium' },
  { label: 'Высокий', value: 'high' },
  { label: 'Критический', value: 'critical' }
]

// Методы испытаний в зависимости от типа
const methodsByType = {
  mechanical: [
    { label: 'Растяжение', value: 'tensile' },
    { label: 'Изгиб', value: 'bend' },
    { label: 'Удар', value: 'impact' },
    { label: 'Твердость', value: 'hardness' }
  ],
  chemical: [
    { label: 'Спектральный анализ', value: 'spectral' },
    { label: 'Химический анализ', value: 'wet_chemistry' },
    { label: 'Рентгенофлуоресцентный', value: 'xrf' }
  ],
  non_destructive: [
    { label: 'УЗК', value: 'ultrasonic' },
    { label: 'МПК', value: 'magnetic_particle' },
    { label: 'ВИК', value: 'visual' },
    { label: 'Рентгеновский', value: 'radiographic' }
  ],
  metallographic: [
    { label: 'Макроструктура', value: 'macro' },
    { label: 'Микроструктура', value: 'micro' },
    { label: 'Размер зерна', value: 'grain_size' }
  ],
  corrosion: [
    { label: 'Солевой туман', value: 'salt_spray' },
    { label: 'Циклические испытания', value: 'cyclic' },
    { label: 'Электрохимические', value: 'electrochemical' }
  ]
}

// Доступные методы для выбранного типа
const availableMethods = computed(() => {
  return form.testType ? methodsByType[form.testType] || [] : []
})

// Сброс метода при смене типа испытания
watch(() => form.testType, (newType, oldType) => {
  if (newType !== oldType) {
    form.testMethod = null
  }
})

// Валидация формы
const validateForm = () => {
  errors.value = {}

  if (!form.materialId) {
    errors.value.materialId = 'Выберите материал'
  }

  if (!form.testType) {
    errors.value.testType = 'Выберите тип испытания'
  }

  return Object.keys(errors.value).length === 0
}

// Загрузка материалов
const loadMaterials = async () => {
  try {
    const response = await materialService.getAll()
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

// Отправка формы
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    const testData = {
      material_id: form.materialId,
      test_type: form.testType,
      test_method: form.testMethod,
      priority: form.priority,
      parameters: {
        temperature: form.temperature,
        sample_count: form.sampleCount,
        expected_strength: form.expectedStrength,
        expected_elongation: form.expectedElongation
      },
      requirements: form.requirements,
      notes: form.notes,
      status: 'planned',
      created_by: 'current_user' // TODO: получать из auth store
    }

    await testService.create(testData)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: 'Испытание создано'
    })

    emit('saved', testData)
    handleCancel()

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

// Отмена
const handleCancel = () => {
  // Сброс формы
  Object.keys(form).forEach(key => {
    if (key === 'materialId') {
      form[key] = props.materialId || null
    } else if (key === 'priority') {
      form[key] = 'medium'
    } else if (key === 'temperature') {
      form[key] = 20
    } else if (key === 'sampleCount') {
      form[key] = 3
    } else {
      form[key] = null
    }
  })
  
  errors.value = {}
  emit('update:visible', false)
  emit('cancel')
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.required::after {
  content: " *";
  color: var(--red-500);
}

h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--primary-color);
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.grid .col-12:first-child h3 {
  margin-top: 0;
}
</style>