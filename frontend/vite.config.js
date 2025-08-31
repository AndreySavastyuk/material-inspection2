import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Выносим крупные библиотеки в отдельные чанки
          'primevue-core': ['primevue/config', 'primevue/button', 'primevue/inputtext', 'primevue/dropdown', 'primevue/dialog'],
          'primevue-table': ['primevue/datatable', 'primevue/column', 'primevue/columngroup'],
          'primevue-form': ['primevue/textarea', 'primevue/inputnumber', 'primevue/checkbox', 'primevue/radiobutton', 'primevue/fileupload', 'primevue/calendar'],
          'primevue-ui': ['primevue/toast', 'primevue/confirmdialog', 'primevue/tag', 'primevue/chip', 'primevue/panel', 'primevue/card', 'primevue/toolbar', 'primevue/menubar', 'primevue/menu', 'primevue/breadcrumb'],
          'primevue-layout': ['primevue/progressbar', 'primevue/divider', 'primevue/tabview', 'primevue/steps', 'primevue/accordion'],
          'chart': ['chart.js', 'vue-chartjs'],
          'utils': ['lodash', 'date-fns', 'qrcode'],
          'router-store': ['vue-router', 'pinia'],
          'vendor': ['vue', 'axios']
        }
      }
    },
    chunkSizeWarningLimit: 600, // Слегка увеличиваем лимит
    target: 'es2015', // Для лучшей совместимости
    minify: 'terser', // Используем terser для лучшего сжатия
    terserOptions: {
      compress: {
        drop_console: true, // Удаляем console.log в продакшене
        drop_debugger: true
      }
    }
  },
  optimizeDeps: {
    include: [
      'vue',
      'vue-router', 
      'pinia',
      'axios',
      'primevue/config',
      'chart.js',
      'date-fns',
      'lodash'
    ]
  }
})
