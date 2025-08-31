<template>
  <div id="app">
    <!-- Верхняя панель с выбором роли -->
    <header class="app-header">
      <div class="header-container">
        <div class="app-logo">
          <i class="pi pi-box"></i>
          <h1>Metal Inspection System</h1>
        </div>

        <div class="header-controls">
          <!-- Выбор роли (без авторизации для разработки) -->
          <div class="role-selector">
            <label>Текущая роль:</label>
            <Dropdown
              v-model="selectedRole"
              :options="roles"
              optionLabel="label"
              optionValue="value"
              placeholder="Выберите роль"
              class="role-dropdown"
              @change="onRoleChange"
            />
          </div>

          <!-- Индикатор статуса -->
          <div class="status-indicator">
            <i class="pi pi-circle-fill" :class="connectionStatus"></i>
            <span>{{ connectionText }}</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Навигационное меню -->
    <nav class="app-nav" v-if="selectedRole">
      <div class="nav-container">
        <router-link
          v-for="item in navigationItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="active"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Основной контент -->
    <main class="app-main">
      <div class="main-container">
        <router-view v-if="selectedRole" />

        <!-- Приветственный экран -->
        <div v-else class="welcome-screen">
          <Card>
            <template #header>
              <div class="welcome-header">
                <i class="pi pi-info-circle"></i>
                <h2>Добро пожаловать в систему контроля металла</h2>
              </div>
            </template>
            <template #content>
              <p>Для начала работы выберите вашу роль в выпадающем меню справа вверху.</p>

              <div class="roles-description">
                <h3>Доступные роли:</h3>
                <ul>
                  <li><strong>Кладовщик</strong> - Приёмка и размещение материалов</li>
                  <li><strong>ОТК</strong> - Контроль качества</li>
                  <li><strong>ЦЗЛ (разрушающий)</strong> - Проведение разрушающих испытаний</li>
                  <li><strong>ЦЗЛ (неразрушающий)</strong> - Проведение неразрушающего контроля</li>
                  <li><strong>Производство</strong> - Запрос и использование материалов</li>
                  <li><strong>Администратор</strong> - Настройка системы и управление</li>
                </ul>
              </div>
            </template>
          </Card>
        </div>
      </div>
    </main>

    <!-- Toast для уведомлений -->
    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useMaterialStore } from '@/stores/material'

import { useToast } from 'primevue/usetoast'

const router = useRouter()
const userStore = useUserStore()
const materialStore = useMaterialStore()
const toast = useToast()

// Роли пользователей
const roles = [
  { label: 'Кладовщик', value: 'warehouse_keeper', icon: 'pi-box' },
  { label: 'ОТК', value: 'quality_control', icon: 'pi-check-circle' },
  { label: 'ЦЗЛ (разрушающий)', value: 'lab_destructive', icon: 'pi-bolt' },
  { label: 'ЦЗЛ (неразрушающий)', value: 'lab_non_destructive', icon: 'pi-eye' },
  { label: 'Производство', value: 'production', icon: 'pi-cog' },
  { label: 'Администратор', value: 'administrator', icon: 'pi-user-plus' }
]

const selectedRole = ref(null)
const isConnected = ref(false)

// Статус подключения
const connectionStatus = computed(() => {
  return isConnected.value ? 'status-online' : 'status-offline'
})

const connectionText = computed(() => {
  return isConnected.value ? 'Подключено' : 'Не подключено'
})

// Навигационные элементы в зависимости от роли
const navigationItems = computed(() => {
  if (!selectedRole.value) return []

  const baseItems = [
    { path: '/', label: 'Главная', icon: 'pi pi-home' },
    { path: '/materials', label: 'Материалы', icon: 'pi pi-box' }
  ]

  const roleSpecificItems = {
    warehouse_keeper: [
      { path: '/receiving', label: 'Приёмка', icon: 'pi pi-download' },
      { path: '/storage', label: 'Склад', icon: 'pi pi-warehouse' }
    ],
    quality_control: [
      { path: '/inspection', label: 'Инспекция', icon: 'pi pi-search' },
      { path: '/reports', label: 'Отчёты', icon: 'pi pi-file' }
    ],
    lab_destructive: [
      { path: '/destructive-tests', label: 'Испытания', icon: 'pi pi-bolt' },
      { path: '/test-results', label: 'Результаты', icon: 'pi pi-chart-bar' }
    ],
    lab_non_destructive: [
      { path: '/non-destructive-tests', label: 'Контроль', icon: 'pi pi-eye' },
      { path: '/test-results', label: 'Результаты', icon: 'pi pi-chart-line' }
    ],
    production: [
      { path: '/material-request', label: 'Запрос материалов', icon: 'pi pi-shopping-cart' },
      { path: '/production-status', label: 'Статус производства', icon: 'pi pi-chart-pie' }
    ],
    administrator: [
      { path: '/workflow-config', label: 'Настройка процессов', icon: 'pi pi-sitemap' },
      { path: '/users', label: 'Пользователи', icon: 'pi pi-users' },
      { path: '/settings', label: 'Настройки', icon: 'pi pi-cog' }
    ]
  }

  return [...baseItems, ...(roleSpecificItems[selectedRole.value] || [])]
})

// Смена роли
const onRoleChange = () => {
  userStore.setRole(selectedRole.value)

  // Показываем уведомление
  toast.add({
    severity: 'success',
    summary: 'Роль изменена',
    detail: `Вы вошли как: ${roles.find(r => r.value === selectedRole.value)?.label}`,
    life: 3000
  })

  // Перенаправляем на главную страницу роли
  router.push('/')

  // Загружаем данные для новой роли
  loadRoleData()
}

// Загрузка данных для роли
const loadRoleData = async () => {
  if (!selectedRole.value) return

  try {
    // Загружаем материалы с учетом роли
    await materialStore.fetchMaterials({ role: selectedRole.value })
  } catch (error) {
    console.error('Error loading role data:', error)
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось загрузить данные',
      life: 5000
    })
  }
}

// Проверка подключения к API
const checkConnection = async () => {
  try {
    const response = await fetch('/api/health')
    isConnected.value = response.ok
  } catch {
    isConnected.value = false
  }
}

// Инициализация
onMounted(() => {
  checkConnection()

  // Проверяем подключение каждые 30 секунд
  setInterval(checkConnection, 30000)

  // Восстанавливаем роль из store
  if (userStore.currentRole) {
    selectedRole.value = userStore.currentRole
    loadRoleData()
  }
})

// Следим за изменением роли в store
watch(() => userStore.currentRole, (newRole) => {
  if (newRole !== selectedRole.value) {
    selectedRole.value = newRole
  }
})
</script>

<style lang="scss">
// Основные переменные
:root {
  --primary-color: #1976d2;
  --secondary-color: #455a64;
  --success-color: #4caf50;
  --warning-color: #ff9800;
  --danger-color: #f44336;
  --info-color: #2196f3;

  --bg-primary: #f5f5f5;
  --bg-secondary: #ffffff;
  --text-primary: #212121;
  --text-secondary: #757575;

  --header-height: 60px;
  --nav-height: 48px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

// Шапка
.app-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid #e0e0e0;
  height: var(--header-height);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);

  .header-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .app-logo {
    display: flex;
    align-items: center;
    gap: 12px;

    i {
      font-size: 28px;
      color: var(--primary-color);
    }

    h1 {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
    }
  }

  .header-controls {
    display: flex;
    align-items: center;
    gap: 24px;

    .role-selector {
      display: flex;
      align-items: center;
      gap: 8px;

      label {
        font-size: 14px;
        color: var(--text-secondary);
      }

      .role-dropdown {
        min-width: 200px;
      }
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;

      .status-online {
        color: var(--success-color);
      }

      .status-offline {
        color: var(--danger-color);
      }
    }
  }
}

// Навигация
.app-nav {
  background: var(--bg-secondary);
  border-bottom: 1px solid #e0e0e0;
  height: var(--nav-height);

  .nav-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 4px;
    text-decoration: none;
    color: var(--text-primary);
    transition: all 0.2s;
    font-size: 14px;

    &:hover {
      background: var(--bg-primary);
    }

    &.active {
      background: var(--primary-color);
      color: white;
    }

    i {
      font-size: 16px;
    }
  }
}

// Основной контент
.app-main {
  flex: 1;
  padding: 24px 0;

  .main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
  }
}

// Экран приветствия
.welcome-screen {
  max-width: 800px;
  margin: 0 auto;

  .welcome-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 20px;

    i {
      font-size: 32px;
      color: var(--info-color);
    }

    h2 {
      font-size: 24px;
      color: var(--text-primary);
    }
  }

  .roles-description {
    margin-top: 24px;

    h3 {
      font-size: 18px;
      margin-bottom: 12px;
      color: var(--text-primary);
    }

    ul {
      list-style: none;

      li {
        padding: 8px 0;
        color: var(--text-secondary);

        strong {
          color: var(--text-primary);
        }
      }
    }
  }
}

// Адаптивность
@media (max-width: 768px) {
  .app-header {
    .header-container {
      flex-direction: column;
      height: auto;
      padding: 12px 20px;
    }

    .app-logo h1 {
      font-size: 18px;
    }
  }

  .app-nav {
    height: auto;

    .nav-container {
      flex-wrap: wrap;
      padding: 8px 20px;
    }
  }
}
</style>