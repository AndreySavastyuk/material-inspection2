import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'

// Импорт глобальных компонентов PrimeVue (опционально)
import Button from 'primevue/button'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import MultiSelect from 'primevue/multiselect'
import Textarea from 'primevue/textarea'
import FileUpload from 'primevue/fileupload'
import Steps from 'primevue/steps'
import Checkbox from 'primevue/checkbox'
import InputNumber from 'primevue/inputnumber'
import AutoComplete from 'primevue/autocomplete'
import Divider from 'primevue/divider'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Timeline from 'primevue/timeline'
import Avatar from 'primevue/avatar'
import SelectButton from 'primevue/selectbutton'
import Menu from 'primevue/menu'
import Message from 'primevue/message'
import Toast from 'primevue/toast'
import Chart from 'primevue/chart'

import App from './App.vue'
import router from './router'

// Стили
import 'primeicons/primeicons.css'
import './assets/styles/main.css'

const app = createApp(App)

// Подключаем плагины
app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      prefix: 'p',
      darkModeSelector: '.dark-mode',
      cssLayer: false
    }
  }
})
app.use(ToastService)

// Регистрируем директивы
app.directive('tooltip', Tooltip)

// Регистрируем глобальные компоненты (опционально)
app.component('Button', Button)
app.component('Card', Card)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('InputText', InputText)
app.component('Dialog', Dialog)
app.component('Tag', Tag)
app.component('Dropdown', Dropdown)
app.component('Calendar', Calendar)
app.component('MultiSelect', MultiSelect)
app.component('Textarea', Textarea)
app.component('FileUpload', FileUpload)
app.component('Steps', Steps)
app.component('Checkbox', Checkbox)
app.component('InputNumber', InputNumber)
app.component('AutoComplete', AutoComplete)
app.component('Divider', Divider)
app.component('TabView', TabView)
app.component('TabPanel', TabPanel)
app.component('Timeline', Timeline)
app.component('Avatar', Avatar)
app.component('SelectButton', SelectButton)
app.component('Menu', Menu)
app.component('Message', Message)
app.component('Toast', Toast)
app.component('Chart', Chart)

app.mount('#app')