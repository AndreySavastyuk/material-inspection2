import api from './api'
import { authService } from './authService'

// Настройка interceptor для автоматического обновления токенов
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  
  failedQueue = []
}

// Response interceptor для обработки истекших токенов
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Если токен уже обновляется, добавляем запрос в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const token = localStorage.getItem('token')

      if (!token) {
        // Нет токена, перенаправляем на логин
        processQueue(error, null)
        return Promise.reject(error)
      }

      try {
        const response = await authService.refreshToken()
        const newToken = response.access_token

        localStorage.setItem('token', newToken)
        authService.setAuthToken(newToken)
        
        processQueue(null, newToken)
        
        // Повторяем оригинальный запрос с новым токеном
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`
        return api(originalRequest)

      } catch (refreshError) {
        // Не удалось обновить токен, очищаем авторизацию
        processQueue(refreshError, null)
        
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        authService.removeAuthToken()
        
        // Перенаправляем на страницу логина
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api