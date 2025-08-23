import api from './api'

export const documentService = {
  async getByMaterialId(materialId) {
    const response = await api.get(`/materials/${materialId}/documents`)
    return response.data
  },

  async upload(materialId, file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post(`/materials/${materialId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  async download(documentId) {
    const response = await api.get(`/documents/${documentId}`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `document_${documentId}`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  async delete(documentId) {
    const response = await api.delete(`/documents/${documentId}`)
    return response.data
  }
}