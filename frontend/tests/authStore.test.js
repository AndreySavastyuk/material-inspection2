import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/authStore'

// Mock authService
vi.mock('@/services/authService', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
    setAuthToken: vi.fn(),
    removeAuthToken: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('authStore', () => {
  let authStore
  let authService

  beforeEach(async () => {
    setActivePinia(createPinia())
    authStore = useAuthStore()
    authService = (await import('@/services/authService')).authService
    
    // Очищаем все моки
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Инициализация состояния', () => {
    it('должен иметь правильное начальное состояние', () => {
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('должен получать токен из localStorage', () => {
      localStorageMock.getItem.mockReturnValue('test-token')
      const store = useAuthStore()
      expect(store.token).toBe('test-token')
    })
  })

  describe('Геттеры', () => {
    beforeEach(() => {
      authStore.user = {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'administrator'
      }
    })

    it('должен возвращать правильную роль пользователя', () => {
      expect(authStore.userRole).toBe('administrator')
    })

    it('должен возвращать правильное имя пользователя', () => {
      expect(authStore.userName).toBe('Test User')
    })

    it('должен возвращать правильный email пользователя', () => {
      expect(authStore.userEmail).toBe('test@example.com')
    })

    it('должен проверять роль пользователя', () => {
      expect(authStore.hasRole('administrator')).toBe(true)
      expect(authStore.hasRole('user')).toBe(false)
    })

    it('должен проверять наличие любой из ролей', () => {
      expect(authStore.hasAnyRole(['administrator', 'user'])).toBe(true)
      expect(authStore.hasAnyRole(['user', 'guest'])).toBe(false)
    })
  })

  describe('Проверка токена', () => {
    it('должен определять истекший токен', () => {
      // Создаем токен с истекшим временем
      const expiredToken = 'header.' + btoa(JSON.stringify({
        exp: Math.floor(Date.now() / 1000) - 100 // 100 секунд назад
      })) + '.signature'
      
      authStore.token = expiredToken
      expect(authStore.isTokenExpired).toBe(true)
    })

    it('должен определять валидный токен', () => {
      // Создаем токен с будущим временем истечения
      const validToken = 'header.' + btoa(JSON.stringify({
        exp: Math.floor(Date.now() / 1000) + 3600 // через час
      })) + '.signature'
      
      authStore.token = validToken
      expect(authStore.isTokenExpired).toBe(false)
    })

    it('должен считать отсутствующий токен истекшим', () => {
      authStore.token = null
      expect(authStore.isTokenExpired).toBe(true)
    })

    it('должен считать невалидный токен истекшим', () => {
      authStore.token = 'invalid-token'
      expect(authStore.isTokenExpired).toBe(true)
    })
  })

  describe('Действие login', () => {
    const mockCredentials = {
      email: 'test@example.com',
      password: 'password'
    }

    const mockResponse = {
      access_token: 'test-token',
      user: {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'administrator'
      }
    }

    it('должен успешно выполнять вход', async () => {
      authService.login.mockResolvedValue(mockResponse)

      const result = await authStore.login(mockCredentials)

      expect(authService.login).toHaveBeenCalledWith(mockCredentials)
      expect(authStore.token).toBe('test-token')
      expect(authStore.user).toEqual(mockResponse.user)
      expect(authStore.isAuthenticated).toBe(true)
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user))
      expect(authService.setAuthToken).toHaveBeenCalledWith('test-token')
      
      expect(result).toEqual(mockResponse)
    })

    it('должен обрабатывать ошибки входа', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Incorrect credentials'
          }
        }
      }
      
      authService.login.mockRejectedValue(mockError)

      await expect(authStore.login(mockCredentials)).rejects.toEqual(mockError)
      
      expect(authStore.error).toBe('Incorrect credentials')
      expect(authStore.loading).toBe(false)
      expect(authStore.isAuthenticated).toBe(false)
    })

    it('должен устанавливать loading состояние', async () => {
      authService.login.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockResponse), 100))
      )

      const loginPromise = authStore.login(mockCredentials)
      expect(authStore.loading).toBe(true)

      await loginPromise
      expect(authStore.loading).toBe(false)
    })
  })

  describe('Действие register', () => {
    const mockUserData = {
      email: 'new@example.com',
      password: 'password',
      full_name: 'New User',
      role: 'user'
    }

    const mockResponse = {
      id: '1',
      email: 'new@example.com',
      full_name: 'New User',
      role: 'user'
    }

    it('должен успешно выполнять регистрацию', async () => {
      authService.register.mockResolvedValue(mockResponse)

      const result = await authStore.register(mockUserData)

      expect(authService.register).toHaveBeenCalledWith(mockUserData)
      expect(result).toEqual(mockResponse)
    })

    it('должен обрабатывать ошибки регистрации', async () => {
      const mockError = {
        response: {
          data: {
            detail: 'Email already exists'
          }
        }
      }
      
      authService.register.mockRejectedValue(mockError)

      await expect(authStore.register(mockUserData)).rejects.toEqual(mockError)
      
      expect(authStore.error).toBe('Email already exists')
      expect(authStore.loading).toBe(false)
    })
  })

  describe('Действие logout', () => {
    beforeEach(() => {
      authStore.token = 'test-token'
      authStore.user = { id: '1', email: 'test@example.com' }
      authStore.isAuthenticated = true
    })

    it('должен успешно выполнять выход', async () => {
      authService.logout.mockResolvedValue()

      await authStore.logout()

      expect(authService.logout).toHaveBeenCalled()
      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.error).toBeNull()
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
      expect(authService.removeAuthToken).toHaveBeenCalled()
    })

    it('должен очищать состояние даже при ошибке logout API', async () => {
      authService.logout.mockRejectedValue(new Error('API Error'))

      await authStore.logout()

      expect(authStore.token).toBeNull()
      expect(authStore.user).toBeNull()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Действие getCurrentUser', () => {
    it('должен получать текущего пользователя', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'administrator'
      }

      authStore.token = 'valid-token'
      authService.getCurrentUser.mockResolvedValue(mockUser)

      const result = await authStore.getCurrentUser()

      expect(authService.getCurrentUser).toHaveBeenCalled()
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.isAuthenticated).toBe(true)
      expect(result).toEqual(mockUser)
    })

    it('должен выходить из системы при ошибке получения пользователя', async () => {
      authStore.token = 'invalid-token'
      authService.getCurrentUser.mockRejectedValue(new Error('Unauthorized'))

      const logoutSpy = vi.spyOn(authStore, 'logout')

      await expect(authStore.getCurrentUser()).rejects.toThrow('Unauthorized')
      expect(logoutSpy).toHaveBeenCalled()
    })

    it('должен выходить если нет токена', async () => {
      authStore.token = null
      const logoutSpy = vi.spyOn(authStore, 'logout')

      const result = await authStore.getCurrentUser()

      expect(logoutSpy).toHaveBeenCalled()
      expect(result).toBeNull()
    })
  })

  describe('Действие refreshToken', () => {
    it('должен обновлять токен', async () => {
      authStore.token = 'old-token'
      const mockResponse = {
        access_token: 'new-token'
      }

      authService.refreshToken.mockResolvedValue(mockResponse)

      const result = await authStore.refreshToken()

      expect(authService.refreshToken).toHaveBeenCalled()
      expect(authStore.token).toBe('new-token')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'new-token')
      expect(authService.setAuthToken).toHaveBeenCalledWith('new-token')
      expect(result).toEqual(mockResponse)
    })

    it('должен выходить из системы при ошибке обновления токена', async () => {
      authStore.token = 'old-token'
      authService.refreshToken.mockRejectedValue(new Error('Refresh failed'))

      const logoutSpy = vi.spyOn(authStore, 'logout')

      await expect(authStore.refreshToken()).rejects.toThrow('Refresh failed')
      expect(logoutSpy).toHaveBeenCalled()
    })

    it('должен выбрасывать ошибку если нет токена', async () => {
      authStore.token = null

      await expect(authStore.refreshToken()).rejects.toThrow('No token to refresh')
    })
  })

  describe('Действие initAuth', () => {
    it('должен инициализировать аутентификацию с существующими данными', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'administrator'
      }

      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'valid-token'
        if (key === 'user') return JSON.stringify(mockUser)
        return null
      })

      authService.getCurrentUser.mockResolvedValue(mockUser)

      await authStore.initAuth()

      expect(authStore.token).toBe('valid-token')
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.isAuthenticated).toBe(true)
      expect(authService.setAuthToken).toHaveBeenCalledWith('valid-token')
    })

    it('должен выходить из системы при ошибке инициализации', async () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'token') return 'invalid-token'
        if (key === 'user') return JSON.stringify({ id: '1' })
        return null
      })

      authService.getCurrentUser.mockRejectedValue(new Error('Invalid token'))

      const logoutSpy = vi.spyOn(authStore, 'logout')

      await authStore.initAuth()

      expect(logoutSpy).toHaveBeenCalled()
    })

    it('не должен делать ничего если нет данных в localStorage', async () => {
      localStorageMock.getItem.mockReturnValue(null)

      await authStore.initAuth()

      expect(authService.setAuthToken).not.toHaveBeenCalled()
      expect(authStore.isAuthenticated).toBe(false)
    })
  })

  describe('Действие clearError', () => {
    it('должен очищать ошибки', () => {
      authStore.error = 'Some error'
      
      authStore.clearError()
      
      expect(authStore.error).toBeNull()
    })
  })
})