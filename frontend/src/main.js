import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Toast from 'primevue/toast'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'
import App from './App.vue'
import router from './router'

// Инициализация API interceptors
import './services/interceptors'

// Стили PrimeVue
import 'primevue/resources/themes/aura-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'

// Основные стили приложения
import './assets/styles/main.css'

const app = createApp(App)

// Подключаем плагины
app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
    ripple: true
})
app.use(ToastService)

// Регистрируем компоненты
app.component('Toast', Toast)
app.component('Dropdown', Dropdown)
app.component('Card', Card)

app.mount('#app')
