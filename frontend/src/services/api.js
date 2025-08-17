import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // В будущем здесь будет добавление токена авторизации
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Обработка ошибок от сервера
      console.error('API Error:', error.response.data)

      if (error.response.status === 401) {
        // Перенаправление на логин
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    } else if (error.request) {
      // Сервер не ответил
      console.error('No response from server')
    } else {
      // Ошибка конфигурации запроса
      console.error('Request error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default api