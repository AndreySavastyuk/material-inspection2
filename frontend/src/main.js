import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Aura from '@primevue/themes/aura'

// Styles
import 'primeicons/primeicons.css'
import './assets/styles/main.css'

// App & Router
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Plugins
app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-mode'
    }
  }
})
app.use(ToastService)

// Mount
app.mount('#app')