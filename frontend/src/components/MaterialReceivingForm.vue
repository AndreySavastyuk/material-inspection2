<template>
  <div class="material-receiving-form">
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center">
          <h2 class="m-0">
            <i class="pi pi-box mr-2"></i>
            Приемка нового материала
          </h2>
          <Tag :value="currentStep.label" :severity="currentStep.severity" />
        </div>
      </template>

      <template #content>
        <!-- Прогресс-бар -->
        <Steps :model="steps" :activeIndex="activeStep" class="mb-4" />

        <!-- Форма -->
        <form @submit.prevent="handleSubmit">
          <!-- Шаг 1: Основная информация -->
          <div v-if="activeStep === 0" class="step-content">
            <div class="grid">
              <!-- Код материала -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="material_code" class="required">Код материала</label>
                  <div class="p-inputgroup">
                    <InputText
                      id="material_code"
                      v-model="form.material_code"
                      :class="{ 'p-invalid': errors.material_code }"
                      placeholder="MAT-2024-001"
                    />
                    <Button
                      icon="pi pi-refresh"
                      @click="generateMaterialCode"
                      v-tooltip="'Сгенерировать код'"
                      :disabled="loading"
                    />
                  </div>
                  <small class="p-error" v-if="errors.material_code">
                    {{ errors.material_code }}
                  </small>
                </div>
              </div>

              <!-- Тип материала -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="material_type" class="required">Тип материала</label>
                  <Dropdown
                    id="material_type"
                    v-model="form.material_type"
                    :options="materialTypes"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Выберите тип"
                    :class="{ 'p-invalid': errors.material_type }"
                  />
                  <small class="p-error" v-if="errors.material_type">
                    {{ errors.material_type }}
                  </small>
                </div>
              </div>

              <!-- Наименование -->
              <div class="col-12">
                <div class="field">
                  <label for="name" class="required">Наименование материала</label>
                  <InputText
                    id="name"
                    v-model="form.name"
                    :class="{ 'p-invalid': errors.name }"
                    placeholder="Например: Лист стальной горячекатаный"
                    class="w-full"
                  />
                  <small class="p-error" v-if="errors.name">
                    {{ errors.name }}
                  </small>
                </div>
              </div>

              <!-- Марка -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="grade">Марка/Сплав</label>
                  <InputText
                    id="grade"
                    v-model="form.grade"
                    placeholder="09Г2С"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Стандарт -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="standard">Стандарт</label>
                  <InputText
                    id="standard"
                    v-model="form.standard"
                    placeholder="ГОСТ 19281-2014"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Размеры -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="dimensions">Размеры</label>
                  <InputText
                    id="dimensions"
                    v-model="form.dimensions"
                    placeholder="10x1500x6000 мм"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Количество -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="quantity" class="required">Количество</label>
                  <InputNumber
                    id="quantity"
                    v-model="form.quantity"
                    :min="0.01"
                    :maxFractionDigits="3"
                    :class="{ 'p-invalid': errors.quantity }"
                    placeholder="0.000"
                  />
                  <small class="p-error" v-if="errors.quantity">
                    {{ errors.quantity }}
                  </small>
                </div>
              </div>

              <!-- Единица измерения -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="unit" class="required">Единица измерения</label>
                  <Dropdown
                    id="unit"
                    v-model="form.unit"
                    :options="units"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Выберите единицу"
                  />
                </div>
              </div>

              <!-- Общий вес -->
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="total_weight">Общий вес (кг)</label>
                  <InputNumber
                    id="total_weight"
                    v-model="form.total_weight"
                    :min="0"
                    :maxFractionDigits="3"
                    placeholder="0.000"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Шаг 2: Информация о поставщике -->
          <div v-if="activeStep === 1" class="step-content">
            <div class="grid">
              <!-- Поставщик -->
              <div class="col-12">
                <div class="field">
                  <label for="supplier" class="required">Поставщик</label>
                  <div class="p-inputgroup">
                    <AutoComplete
                      id="supplier"
                      v-model="form.supplier"
                      :suggestions="filteredSuppliers"
                      @complete="searchSupplier"
                      :class="{ 'p-invalid': errors.supplier }"
                      placeholder="Начните вводить название поставщика"
                      class="flex-1"
                    />
                    <Button
                      icon="pi pi-plus"
                      @click="showNewSupplierDialog = true"
                      v-tooltip="'Добавить нового поставщика'"
                    />
                  </div>
                  <small class="p-error" v-if="errors.supplier">
                    {{ errors.supplier }}
                  </small>
                </div>
              </div>

              <!-- Номер сертификата поставщика -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="supplier_certificate_number">Номер сертификата поставщика</label>
                  <InputText
                    id="supplier_certificate_number"
                    v-model="form.supplier_certificate_number"
                    placeholder="СК-12345/2024"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Номер партии -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="batch_number">Номер партии</label>
                  <InputText
                    id="batch_number"
                    v-model="form.batch_number"
                    placeholder="BATCH-2024-001"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Номер плавки -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="heat_number">Номер плавки</label>
                  <InputText
                    id="heat_number"
                    v-model="form.heat_number"
                    placeholder="П-123456"
                    class="w-full"
                  />
                </div>
              </div>

              <!-- Место хранения -->
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="current_location">Место размещения на складе</label>
                  <Dropdown
                    id="current_location"
                    v-model="form.current_location"
                    :options="storageLocations"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Выберите место"
                    :filter="true"
                  />
                </div>
              </div>

              <!-- Примечания -->
              <div class="col-12">
                <div class="field">
                  <label for="notes">Примечания</label>
                  <Textarea
                    id="notes"
                    v-model="form.notes"
                    rows="3"
                    class="w-full"
                    placeholder="Дополнительная информация о материале..."
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Шаг 3: Документы и файлы -->
          <div v-if="activeStep === 2" class="step-content">
            <div class="grid">
              <!-- Загрузка сертификата поставщика -->
              <div class="col-12">
                <div class="field">
                  <label>Сертификат качества поставщика</label>
                  <FileUpload
                    ref="supplierCertUpload"
                    name="supplier_certificate"
                    :multiple="false"
                    accept=".pdf,.jpg,.jpeg,.png"
                    :maxFileSize="10000000"
                    @select="onSupplierCertSelect"
                    @remove="onSupplierCertRemove"
                    :showUploadButton="false"
                    :showCancelButton="false"
                  >
                    <template #header>
                      <div class="flex align-items-center justify-content-between w-full">
                        <span class="text-sm text-500">
                          Максимальный размер: 10MB (PDF, JPG, PNG)
                        </span>
                      </div>
                    </template>
                    <template #content="{ files, removeFileCallback }">
                      <div v-if="files.length > 0">
                        <div class="flex align-items-center p-3 border-round mb-2 surface-100">
                          <i class="pi pi-file-pdf text-4xl mr-3"></i>
                          <div class="flex-1">
                            <div class="font-semibold">{{ files[0].name }}</div>
                            <div class="text-sm text-500">{{ formatFileSize(files[0].size) }}</div>
                          </div>
                          <Button
                            icon="pi pi-times"
                            @click="removeFileCallback(0)"
                            outlined
                            rounded
                            severity="danger"
                            size="small"
                          />
                        </div>
                      </div>
                    </template>
                    <template #empty>
                      <div class="flex align-items-center justify-content-center flex-column">
                        <i class="pi pi-cloud-upload text-5xl text-400 mb-3"></i>
                        <p class="text-lg text-600">Перетащите файл сюда или нажмите для выбора</p>
                      </div>
                    </template>
                  </FileUpload>
                </div>
              </div>

              <!-- Дополнительные документы -->
              <div class="col-12">
                <div class="field">
                  <label>Дополнительные документы</label>
                  <FileUpload
                    ref="additionalDocsUpload"
                    name="additional_docs"
                    :multiple="true"
                    accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
                    :maxFileSize="10000000"
                    @select="onAdditionalDocsSelect"
                    @remove="onAdditionalDocsRemove"
                    :showUploadButton="false"
                    :showCancelButton="false"
                  >
                    <template #header>
                      <div class="flex align-items-center justify-content-between w-full">
                        <span class="text-sm text-500">
                          Можно загрузить несколько файлов (PDF, JPG, PNG, DOC, XLS)
                        </span>
                      </div>
                    </template>
                    <template #content="{ files, removeFileCallback }">
                      <div v-if="files.length > 0">
                        <div
                          v-for="(file, index) in files"
                          :key="file.name + file.type + file.size"
                          class="flex align-items-center p-3 border-round mb-2 surface-100"
                        >
                          <i :class="getFileIcon(file.type)" class="text-4xl mr-3"></i>
                          <div class="flex-1">
                            <div class="font-semibold">{{ file.name }}</div>
                            <div class="text-sm text-500">{{ formatFileSize(file.size) }}</div>
                          </div>
                          <Button
                            icon="pi pi-times"
                            @click="removeFileCallback(index)"
                            outlined
                            rounded
                            severity="danger"
                            size="small"
                          />
                        </div>
                      </div>
                    </template>
                    <template #empty>
                      <div class="flex align-items-center justify-content-center flex-column">
                        <i class="pi pi-cloud-upload text-5xl text-400 mb-3"></i>
                        <p class="text-lg text-600">Перетащите файлы сюда или нажмите для выбора</p>
                      </div>
                    </template>
                  </FileUpload>
                </div>
              </div>

              <!-- Требования к испытаниям -->
              <div class="col-12">
                <div class="field">
                  <label>Требуемые испытания</label>
                  <MultiSelect
                    v-model="form.required_tests"
                    :options="testTypes"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Выберите необходимые испытания"
                    class="w-full"
                    display="chip"
                  />
                  <small class="text-500">
                    Выберите испытания, которые необходимо провести для данного материала
                  </small>
                </div>
              </div>

              <!-- Требует карантина -->
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox
                    id="requires_quarantine"
                    v-model="form.metadata.requires_quarantine"
                    :binary="true"
                  />
                  <label for="requires_quarantine" class="ml-2">
                    Требуется карантинное хранение
                  </label>
                </div>
              </div>

              <!-- Срочная приемка -->
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox
                    id="is_urgent"
                    v-model="form.metadata.is_urgent"
                    :binary="true"
                  />
                  <label for="is_urgent" class="ml-2">
                    Срочная приемка (приоритетная обработка)
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Шаг 4: Подтверждение -->
          <div v-if="activeStep === 3" class="step-content">
            <div class="confirmation-summary">
              <h3>Проверьте введенные данные</h3>

              <div class="summary-section">
                <h4><i class="pi pi-info-circle mr-2"></i>Основная информация</h4>
                <div class="summary-grid">
                  <div class="summary-item">
                    <span class="label">Код материала:</span>
                    <span class="value">{{ form.material_code }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Тип:</span>
                    <span class="value">{{ getMaterialTypeLabel(form.material_type) }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Наименование:</span>
                    <span class="value">{{ form.name }}</span>
                  </div>
                  <div class="summary-item" v-if="form.grade">
                    <span class="label">Марка:</span>
                    <span class="value">{{ form.grade }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Количество:</span>
                    <span class="value">{{ form.quantity }} {{ form.unit }}</span>
                  </div>
                  <div class="summary-item" v-if="form.total_weight">
                    <span class="label">Общий вес:</span>
                    <span class="value">{{ form.total_weight }} кг</span>
                  </div>
                </div>
              </div>

              <div class="summary-section">
                <h4><i class="pi pi-truck mr-2"></i>Информация о поставке</h4>
                <div class="summary-grid">
                  <div class="summary-item">
                    <span class="label">Поставщик:</span>
                    <span class="value">{{ form.supplier }}</span>
                  </div>
                  <div class="summary-item" v-if="form.supplier_certificate_number">
                    <span class="label">Сертификат поставщика:</span>
                    <span class="value">{{ form.supplier_certificate_number }}</span>
                  </div>
                  <div class="summary-item" v-if="form.batch_number">
                    <span class="label">Партия:</span>
                    <span class="value">{{ form.batch_number }}</span>
                  </div>
                  <div class="summary-item" v-if="form.heat_number">
                    <span class="label">Плавка:</span>
                    <span class="value">{{ form.heat_number }}</span>
                  </div>
                </div>
              </div>

              <div class="summary-section" v-if="uploadedFiles.length > 0">
                <h4><i class="pi pi-file mr-2"></i>Загруженные документы</h4>
                <div class="uploaded-files-list">
                  <div v-for="file in uploadedFiles" :key="file.name" class="file-item">
                    <i :class="getFileIcon(file.type)" class="mr-2"></i>
                    {{ file.name }}
                  </div>
                </div>
              </div>

              <div class="summary-section" v-if="form.required_tests.length > 0">
                <h4><i class="pi pi-check-circle mr-2"></i>Требуемые испытания</h4>
                <div class="tests-list">
                  <Tag
                    v-for="test in form.required_tests"
                    :key="test"
                    :value="getTestLabel(test)"
                    severity="info"
                    class="mr-2 mb-2"
                  />
                </div>
              </div>

              <Message severity="info" :closable="false" class="mt-3">
                <i class="pi pi-info-circle mr-2"></i>
                После подтверждения материал будет зарегистрирован в системе и направлен на дальнейшую обработку
              </Message>
            </div>
          </div>

          <!-- Кнопки навигации -->
          <div class="form-actions">
            <Button
              label="Назад"
              icon="pi pi-chevron-left"
              @click="previousStep"
              :disabled="activeStep === 0 || loading"
              severity="secondary"
            />

            <div class="flex gap-2">
              <Button
                label="Отмена"
                icon="pi pi-times"
                @click="handleCancel"
                :disabled="loading"
                severity="secondary"
                outlined
              />

              <Button
                v-if="activeStep < 3"
                label="Далее"
                icon="pi pi-chevron-right"
                iconPos="right"
                @click="nextStep"
                :disabled="loading"
              />

              <Button
                v-if="activeStep === 3"
                label="Подтвердить приемку"
                icon="pi pi-check"
                iconPos="right"
                @click="handleSubmit"
                :loading="loading"
                severity="success"
              />
            </div>
          </div>
        </form>
      </template>
    </Card>

    <!-- Диалог добавления нового поставщика -->
    <Dialog
      v-model:visible="showNewSupplierDialog"
      header="Добавить нового поставщика"
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="field">
        <label for="new_supplier_name" class="required">Название поставщика</label>
        <InputText
          id="new_supplier_name"
          v-model="newSupplier.name"
          class="w-full"
          placeholder="ООО 'МеталлПоставка'"
        />
      </div>
      <div class="field">
        <label for="new_supplier_inn">ИНН</label>
        <InputText
          id="new_supplier_inn"
          v-model="newSupplier.inn"
          class="w-full"
          placeholder="1234567890"
        />
      </div>
      <div class="field">
        <label for="new_supplier_contact">Контактное лицо</label>
        <InputText
          id="new_supplier_contact"
          v-model="newSupplier.contact"
          class="w-full"
          placeholder="Иванов И.И."
        />
      </div>
      <div class="field">
        <label for="new_supplier_phone">Телефон</label>
        <InputText
          id="new_supplier_phone"
          v-model="newSupplier.phone"
          class="w-full"
          placeholder="+7 (999) 123-45-67"
        />
      </div>

      <template #footer>
        <Button
          label="Отмена"
          icon="pi pi-times"
          @click="showNewSupplierDialog = false"
          severity="secondary"
          outlined
        />
        <Button
          label="Добавить"
          icon="pi pi-check"
          @click="addNewSupplier"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useRouter } from 'vue-router'
import { materialService } from '@/services/materialService'

const toast = useToast()
const router = useRouter()

// Состояние формы
const loading = ref(false)
const activeStep = ref(0)
const showNewSupplierDialog = ref(false)

// Шаги формы
const steps = ref([
  { label: 'Основная информация', icon: 'pi pi-info-circle' },
  { label: 'Поставщик', icon: 'pi pi-truck' },
  { label: 'Документы', icon: 'pi pi-file' },
  { label: 'Подтверждение', icon: 'pi pi-check' }
])

// Текущий шаг для отображения статуса
const currentStep = computed(() => {
  const stepLabels = [
    { label: 'Ввод данных', severity: 'info' },
    { label: 'Информация о поставке', severity: 'info' },
    { label: 'Загрузка документов', severity: 'warning' },
    { label: 'Проверка данных', severity: 'success' }
  ]
  return stepLabels[activeStep.value]
})

// Данные формы
const form = reactive({
  material_code: '',
  material_type: '',
  name: '',
  grade: '',
  standard: '',
  dimensions: '',
  supplier: '',
  supplier_certificate_number: '',
  batch_number: '',
  heat_number: '',
  quantity: null,
  unit: 'kg',
  total_weight: null,
  current_location: '',
  notes: '',
  required_tests: [],
  metadata: {
    requires_quarantine: false,
    is_urgent: false,
    invoice_number: '',
    received_by: null
  }
})

// Ошибки валидации
const errors = reactive({
  material_code: '',
  material_type: '',
  name: '',
  quantity: '',
  supplier: ''
})

// Загруженные файлы
const uploadedFiles = ref([])
const supplierCertificate = ref(null)
const additionalDocs = ref([])

// Новый поставщик
const newSupplier = reactive({
  name: '',
  inn: '',
  contact: '',
  phone: ''
})

// Справочники
const materialTypes = ref([
  { label: 'Листовой прокат', value: 'sheet' },
  { label: 'Сортовой прокат', value: 'profile' },
  { label: 'Трубы', value: 'pipe' },
  { label: 'Проволока', value: 'wire' },
  { label: 'Арматура', value: 'rebar' },
  { label: 'Прочее', value: 'other' }
])

const units = ref([
  { label: 'Килограммы', value: 'kg' },
  { label: 'Тонны', value: 't' },
  { label: 'Метры', value: 'm' },
  { label: 'Квадратные метры', value: 'm2' },
  { label: 'Штуки', value: 'pcs' },
  { label: 'Листы', value: 'sheets' }
])

const storageLocations = ref([
  { label: 'Склад 1 - Зона А', value: 'storage1_zoneA' },
  { label: 'Склад 1 - Зона Б', value: 'storage1_zoneB' },
  { label: 'Склад 2 - Зона А', value: 'storage2_zoneA' },
  { label: 'Склад 2 - Зона Б', value: 'storage2_zoneB' },
  { label: 'Карантинная зона', value: 'quarantine' },
  { label: 'Зона временного хранения', value: 'temporary' }
])

const testTypes = ref([
  { label: 'Химический анализ', value: 'chemical' },
  { label: 'Механические испытания', value: 'mechanical' },
  { label: 'Испытания на растяжение', value: 'tensile' },
  { label: 'Испытания на удар', value: 'impact' },
  { label: 'Измерение твердости', value: 'hardness' },
  { label: 'Ультразвуковой контроль', value: 'ultrasonic' },
  { label: 'Магнитопорошковый контроль', value: 'magnetic' },
  { label: 'Визуальный контроль', value: 'visual' },
  { label: 'Измерение толщины', value: 'thickness' },
  { label: 'Металлография', value: 'metallography' }
])

const suppliers = ref([
  'ООО "МеталлСервис"',
  'АО "СтальИнвест"',
  'ООО "ПромМеталл"',
  'ПАО "Северсталь"',
  'ООО "МеталлоТорг"'
])

const filteredSuppliers = ref([])

// Методы
const generateMaterialCode = () => {
  const year = new Date().getFullYear()
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  form.material_code = `MAT-${year}-${random}`

  toast.add({
    severity: 'success',
    summary: 'Код сгенерирован',
    detail: `Новый код: ${form.material_code}`,
    life: 3000
  })
}

const searchSupplier = (event) => {
  const query = event.query.toLowerCase()
  filteredSuppliers.value = suppliers.value.filter(s =>
    s.toLowerCase().includes(query)
  )
}

const validateStep = (step) => {
  // Очищаем предыдущие ошибки
  Object.keys(errors).forEach(key => errors[key] = '')

  let isValid = true

  if (step === 0) {
    // Валидация основной информации
    if (!form.material_code) {
      errors.material_code = 'Код материала обязателен'
      isValid = false
    }
    if (!form.material_type) {
      errors.material_type = 'Выберите тип материала'
      isValid = false
    }
    if (!form.name) {
      errors.name = 'Наименование обязательно'
      isValid = false
    }
    if (!form.quantity || form.quantity <= 0) {
      errors.quantity = 'Укажите корректное количество'
      isValid = false
    }
  } else if (step === 1) {
    // Валидация информации о поставщике
    if (!form.supplier) {
      errors.supplier = 'Укажите поставщика'
      isValid = false
    }
  }

  return isValid
}

const nextStep = () => {
  if (validateStep(activeStep.value)) {
    if (activeStep.value < steps.value.length - 1) {
      activeStep.value++
    }
  } else {
    toast.add({
      severity: 'error',
      summary: 'Ошибка валидации',
      detail: 'Заполните все обязательные поля',
      life: 3000
    })
  }
}

const previousStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true

    // Подготовка данных для отправки
    const materialData = {
      ...form,
      metadata: {
        ...form.metadata,
        uploaded_files: uploadedFiles.value.map(f => ({
          name: f.name,
          type: f.type,
          size: f.size
        }))
      }
    }

    // Отправка на сервер
    const response = await materialService.create(materialData)

    toast.add({
      severity: 'success',
      summary: 'Успешно',
      detail: `Материал ${form.material_code} успешно зарегистрирован`,
      life: 5000
    })

    // Переход к списку материалов
    setTimeout(() => {
      router.push('/materials')
    }, 1500)

  } catch (error) {
    console.error('Ошибка при создании материала:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось зарегистрировать материал',
      life: 5000
    })
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.push('/materials')
}

const onSupplierCertSelect = (event) => {
  supplierCertificate.value = event.files[0]
  uploadedFiles.value.push(event.files[0])
}

const onSupplierCertRemove = () => {
  supplierCertificate.value = null
  uploadedFiles.value = uploadedFiles.value.filter(f => f !== supplierCertificate.value)
}

const onAdditionalDocsSelect = (event) => {
  additionalDocs.value = [...event.files]
  uploadedFiles.value = [...uploadedFiles.value, ...event.files]
}

const onAdditionalDocsRemove = (event) => {
  const file = event.file
  additionalDocs.value = additionalDocs.value.filter(f => f !== file)
  uploadedFiles.value = uploadedFiles.value.filter(f => f !== file)
}

const addNewSupplier = () => {
  if (newSupplier.name) {
    suppliers.value.push(newSupplier.name)
    form.supplier = newSupplier.name

    // Сохранить информацию о новом поставщике в metadata
    form.metadata.new_supplier = { ...newSupplier }

    // Очистить форму и закрыть диалог
    Object.keys(newSupplier).forEach(key => newSupplier[key] = '')
    showNewSupplierDialog.value = false

    toast.add({
      severity: 'success',
      summary: 'Поставщик добавлен',
      detail: `${form.supplier} успешно добавлен в систему`,
      life: 3000
    })
  }
}

// Вспомогательные функции
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getFileIcon = (fileType) => {
  if (fileType.includes('pdf')) return 'pi pi-file-pdf text-red-500'
  if (fileType.includes('image')) return 'pi pi-image text-blue-500'
  if (fileType.includes('word')) return 'pi pi-file-word text-blue-600'
  if (fileType.includes('sheet') || fileType.includes('excel')) return 'pi pi-file-excel text-green-600'
  return 'pi pi-file text-gray-500'
}

const getMaterialTypeLabel = (value) => {
  const type = materialTypes.value.find(t => t.value === value)
  return type ? type.label : value
}

const getTestLabel = (value) => {
  const test = testTypes.value.find(t => t.value === value)
  return test ? test.label : value
}

// Хук жизненного цикла
onMounted(() => {
  // Генерируем код материала при загрузке
  generateMaterialCode()
})
</script>

<style scoped>
.material-receiving-form {
  max-width: 1200px;
  margin: 0 auto;
}

.step-content {
  min-height: 400px;
  padding: 1rem 0;
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.field label.required::after {
  content: ' *';
  color: var(--red-500);
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
}

/* Стили для подтверждения */
.confirmation-summary {
  padding: 1rem;
}

.confirmation-summary h3 {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
}

.summary-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 6px;
}

.summary-section h4 {
  margin-bottom: 1rem;
  color: var(--text-color);
  font-size: 1.1rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-item .label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.summary-item .value {
  font-weight: 500;
  color: var(--text-color);
}

.uploaded-files-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  padding: 0.5rem;
  background: var(--surface-0);
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.tests-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
    gap: 1rem;
  }

  .form-actions > * {
    width: 100%;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>