import api from './api'

export const userService = {
  async getAll() {
    const response = await api.get('/users')
    return response.data
  },

  async getLabUsers() {
    const response = await api.get('/users/lab')
    return response.data
  },

  async getById(id) {
    const response = await api.get(`/users/${id}`)
    return response.data
  }
}