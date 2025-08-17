import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export const useMaterialStore = defineStore('material', () => {
  const materials = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchMaterials(filters = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/materials', { params: filters })
      materials.value = response.data.items || []
      return response.data
    } catch (err) {
      error.value = err.message
      console.error('Error fetching materials:', err)
    } finally {
      loading.value = false
    }
  }

  async function createMaterial(data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/materials', data)
      materials.value.unshift(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateMaterial(id, data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.patch(`/materials/${id}`, data)
      const index = materials.value.findIndex(m => m.id === id)
      if (index !== -1) {
        materials.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteMaterial(id) {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/materials/${id}`)
      materials.value = materials.value.filter(m => m.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    materials,
    loading,
    error,
    fetchMaterials,
    createMaterial,
    updateMaterial,
    deleteMaterial
  }
})