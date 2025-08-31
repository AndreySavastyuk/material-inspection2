import { defineStore } from 'pinia'
import { authService } from '@/services/authService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
    loading: false,
    error: null
  }),

  getters: {
    userRole: (state) => state.user?.role,
    userName: (state) => state.user?.full_name,
    userEmail: (state) => state.user?.email,
    
    hasRole: (state) => (role) => {
      return state.user?.role === role
    },
    
    hasAnyRole: (state) => (roles) => {
      return roles.includes(state.user?.role)
    },
    
    isTokenExpired: (state) => {
      if (!state.token) return true
      
      try {
        const payload = JSON.parse(atob(state.token.split('.')[1]))
        return payload.exp * 1000 < Date.now()
      } catch {
        return true
      }
    }
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const response = await authService.login(credentials)
        
        this.token = response.access_token
        this.user = response.user
        this.isAuthenticated = true
        
        localStorage.setItem('token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
        
        // Установка токена в заголовок axios
        authService.setAuthToken(response.access_token)
        
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка входа'
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await authService.register(userData)
        return response
      } catch (error) {
        this.error = error.response?.data?.detail || 'Ошибка регистрации'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      
      try {
        if (this.token) {
          await authService.logout()
        }
      } catch (error) {
        console.warn('Logout error:', error)
      } finally {
        this.token = null
        this.user = null
        this.isAuthenticated = false
        this.error = null
        this.loading = false
        
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        // Удаление токена из заголовка axios
        authService.removeAuthToken()
      }
    },

    async getCurrentUser() {
      if (!this.token || this.isTokenExpired) {
        await this.logout()
        return null
      }
      
      try {
        const user = await authService.getCurrentUser()
        this.user = user
        this.isAuthenticated = true
        return user
      } catch (error) {
        await this.logout()
        throw error
      }
    },

    async refreshToken() {
      if (!this.token) {
        throw new Error('No token to refresh')
      }
      
      try {
        const response = await authService.refreshToken()
        this.token = response.access_token
        localStorage.setItem('token', response.access_token)
        authService.setAuthToken(response.access_token)
        return response
      } catch (error) {
        await this.logout()
        throw error
      }
    },

    async initAuth() {
      const token = localStorage.getItem('token')
      const userData = localStorage.getItem('user')
      
      if (token && userData) {
        try {
          this.token = token
          this.user = JSON.parse(userData)
          
          authService.setAuthToken(token)
          
          // Проверяем токен
          if (this.isTokenExpired) {
            await this.refreshToken()
          } else {
            // Проверяем актуальность данных пользователя
            await this.getCurrentUser()
          }
          
          this.isAuthenticated = true
        } catch (error) {
          console.warn('Auth initialization failed:', error)
          await this.logout()
        }
      }
    },

    clearError() {
      this.error = null
    }
  }
})