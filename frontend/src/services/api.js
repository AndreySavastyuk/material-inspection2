import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Интерцептор запросов для добавления токена
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.token

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Логирование запросов в режиме разработки
    if (import.meta.env.DEV) {
      console.log(`🚀 ${config.method?.toUpperCase()} ${config.url}`, config.data)
    }

    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Интерцептор ответов для обработки ошибок
api.interceptors.response.use(
  (response) => {
    // Логирование ответов в режиме разработки
    if (import.meta.env.DEV) {
      console.log(`✅ Response from ${response.config.url}:`, response.data)
    }
    return response
  },
  async (error) => {
    const authStore = useAuthStore()

    // Обработка различных типов ошибок
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // Токен истек или невалидный
          console.error('Unauthorized - redirecting to login')
          authStore.logout()
          window.location.href = '/login'
          break

        case 403:
          console.error('Forbidden - insufficient permissions')
          // Можно показать уведомление о недостаточных правах
          break

        case 404:
          console.error('Resource not found')
          break

        case 422:
          console.error('Validation error:', error.response.data)
          break

        case 500:
          console.error('Server error')
          break

        default:
          console.error(`Error ${error.response.status}:`, error.response.data)
      }
    } else if (error.request) {
      // Запрос был сделан, но ответ не получен
      console.error('No response from server:', error.request)
    } else {
      // Что-то произошло при настройке запроса
      console.error('Request setup error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default api

// Вспомогательные функции для работы с API

/**
 * Обработка ошибок API с извлечением сообщения
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail) {
    // FastAPI формат ошибки
    if (typeof error.response.data.detail === 'string') {
      return error.response.data.detail
    }
    // Если detail - массив (ошибки валидации)
    if (Array.isArray(error.response.data.detail)) {
      return error.response.data.detail
        .map(err => `${err.loc.join('.')}: ${err.msg}`)
        .join(', ')
    }
  }

  if (error.response?.data?.message) {
    return error.response.data.message
  }

  if (error.message) {
    return error.message
  }

  return 'Произошла неизвестная ошибка'
}

/**
 * Создание query string из объекта параметров
 */
export const buildQueryString = (params) => {
  const query = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      if (Array.isArray(value)) {
        value.forEach(v => query.append(key, v))
      } else {
        query.append(key, value)
      }
    }
  })

  return query.toString()
}

/**
 * Обертка для загрузки файлов
 */
export const uploadFile = async (url, file, additionalData = {}) => {
  const formData = new FormData()
  formData.append('file', file)

  // Добавляем дополнительные данные
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value)
  })

  return api.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * Обертка для скачивания файлов
 */
export const downloadFile = async (url, filename) => {
  const response = await api.get(url, {
    responseType: 'blob'
  })

  // Создаем ссылку для скачивания
  const downloadUrl = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = downloadUrl
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()

  // Освобождаем память
  window.URL.revokeObjectURL(downloadUrl)

  return response
}