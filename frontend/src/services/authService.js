import api from './api'

export const authService = {
  /**
   * Вход в систему
   * @param {Object} credentials - учетные данные {email, password}
   * @returns {Promise} - токен и данные пользователя
   */
  async login(credentials) {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  /**
   * Регистрация пользователя
   * @param {Object} userData - данные пользователя
   * @returns {Promise} - данные созданного пользователя
   */
  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  /**
   * Выход из системы
   * @returns {Promise}
   */
  async logout() {
    const response = await api.post('/auth/logout')
    return response.data
  },

  /**
   * Получить данные текущего пользователя
   * @returns {Promise} - данные пользователя
   */
  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  /**
   * Обновить токен
   * @returns {Promise} - новый токен
   */
  async refreshToken() {
    const response = await api.post('/auth/refresh')
    return response.data
  },

  /**
   * Установить токен авторизации в заголовки axios
   * @param {string} token - JWT токен
   */
  setAuthToken(token) {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    } else {
      delete api.defaults.headers.common['Authorization']
    }
  },

  /**
   * Удалить токен авторизации из заголовков
   */
  removeAuthToken() {
    delete api.defaults.headers.common['Authorization']
  },

  /**
   * Проверить статус токена
   * @returns {Promise} - статус токена
   */
  async checkTokenStatus() {
    try {
      const response = await api.get('/auth/me')
      return { valid: true, user: response.data }
    } catch (error) {
      return { valid: false, error: error.response?.data }
    }
  },

  /**
   * Сменить пароль
   * @param {Object} passwordData - {old_password, new_password}
   * @returns {Promise}
   */
  async changePassword(passwordData) {
    const response = await api.post('/auth/change-password', passwordData)
    return response.data
  },

  /**
   * Запросить сброс пароля
   * @param {string} email - email пользователя
   * @returns {Promise}
   */
  async requestPasswordReset(email) {
    const response = await api.post('/auth/forgot-password', { email })
    return response.data
  },

  /**
   * Подтвердить сброс пароля
   * @param {Object} resetData - {token, new_password}
   * @returns {Promise}
   */
  async confirmPasswordReset(resetData) {
    const response = await api.post('/auth/reset-password', resetData)
    return response.data
  },

  /**
   * Проверить валидность email
   * @param {string} email
   * @returns {Promise}
   */
  async checkEmailAvailability(email) {
    const response = await api.post('/auth/check-email', { email })
    return response.data
  },

  /**
   * Активировать учетную запись
   * @param {string} token - токен активации
   * @returns {Promise}
   */
  async activateAccount(token) {
    const response = await api.post(`/auth/activate/${token}`)
    return response.data
  },

  /**
   * Отправить повторное письмо активации
   * @param {string} email
   * @returns {Promise}
   */
  async resendActivation(email) {
    const response = await api.post('/auth/resend-activation', { email })
    return response.data
  }
}


export default authService