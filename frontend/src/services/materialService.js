import api from './api'

export const materialService = {
  /**
   * Получить список материалов с фильтрацией и пагинацией
   */
  async getAll(params = {}) {
    const queryParams = new URLSearchParams()

    // Добавляем параметры фильтрации
    if (params.search) queryParams.append('search', params.search)
    if (params.status) queryParams.append('status', params.status)
    if (params.material_type) queryParams.append('material_type', params.material_type)
    if (params.supplier) queryParams.append('supplier', params.supplier)
    if (params.page) queryParams.append('page', params.page)
    if (params.per_page) queryParams.append('per_page', params.per_page)
    if (params.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params.sort_order) queryParams.append('sort_order', params.sort_order)

    const response = await api.get(`/materials?${queryParams.toString()}`)
    return response.data
  },

  /**
   * Получить материал по ID
   */
  async getById(id) {
    const response = await api.get(`/materials/${id}`)
    return response.data
  },

  /**
   * Создать новый материал
   */
  async create(data) {
    // Подготовка данных
    const materialData = {
      material_code: data.material_code,
      material_type: data.material_type,
      name: data.name,
      grade: data.grade || null,
      standard: data.standard || null,
      dimensions: data.dimensions || null,
      supplier: data.supplier,
      supplier_certificate_number: data.supplier_certificate_number || null,
      batch_number: data.batch_number || null,
      heat_number: data.heat_number || null,
      quantity: parseFloat(data.quantity),
      unit: data.unit,
      total_weight: data.total_weight ? parseFloat(data.total_weight) : null,
      current_location: data.current_location || null,
      notes: data.notes || null,
      metadata: data.metadata || {}
    }

    const response = await api.post('/materials', materialData)
    return response.data
  },

  /**
   * Обновить материал
   */
  async update(id, data) {
    const response = await api.put(`/materials/${id}`, data)
    return response.data
  },

  /**
   * Удалить материал
   */
  async delete(id) {
    const response = await api.delete(`/materials/${id}`)
    return response.data
  },

  /**
   * Изменить статус материала (workflow)
   */
  async changeStatus(id, transition, notes = '') {
    const response = await api.post(`/materials/${id}/transition`, {
      transition,
      notes
    })
    return response.data
  },

  /**
   * Получить историю изменений материала
   */
  async getHistory(id) {
    const response = await api.get(`/materials/${id}/history`)
    return response.data
  },

  /**
   * Получить доступные переходы для материала
   */
  async getAvailableTransitions(id) {
    const response = await api.get(`/materials/${id}/transitions`)
    return response.data
  },

  /**
   * Загрузить документы для материала
   */
  async uploadDocuments(id, files) {
    const formData = new FormData()

    files.forEach((file, index) => {
      formData.append(`files`, file)
    })

    const response = await api.post(`/materials/${id}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Получить документы материала
   */
  async getDocuments(id) {
    const response = await api.get(`/materials/${id}/documents`)
    return response.data
  },

  /**
   * Скачать документ
   */
  async downloadDocument(materialId, documentId) {
    const response = await api.get(`/materials/${materialId}/documents/${documentId}`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Получить статистику по материалам
   */
  async getStatistics() {
    const response = await api.get('/materials/statistics')
    return response.data
  },

  /**
   * Получить список поставщиков
   */
  async getSuppliers() {
    const response = await api.get('/materials/suppliers')
    return response.data
  },

  /**
   * Экспортировать материалы в Excel
   */
  async exportToExcel(params = {}) {
    const queryParams = new URLSearchParams()

    // Добавляем параметры фильтрации для экспорта
    if (params.status) queryParams.append('status', params.status)
    if (params.material_type) queryParams.append('material_type', params.material_type)
    if (params.date_from) queryParams.append('date_from', params.date_from)
    if (params.date_to) queryParams.append('date_to', params.date_to)

    const response = await api.get(`/materials/export?${queryParams.toString()}`, {
      responseType: 'blob'
    })

    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `materials_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Генерировать уникальный код материала
   */
  async generateCode(prefix = 'MAT') {
    const response = await api.get(`/materials/generate-code?prefix=${prefix}`)
    return response.data
  },

  /**
   * Проверить существование кода материала
   */
  async checkCodeExists(code) {
    try {
      const response = await api.get(`/materials/check-code/${code}`)
      return response.data.exists
    } catch (error) {
      return false
    }
  },

  /**
   * Получить шаблон для импорта
   */
  async getImportTemplate() {
    const response = await api.get('/materials/import-template', {
      responseType: 'blob'
    })

    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'material_import_template.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Импортировать материалы из Excel
   */
  async importFromExcel(file) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post('/materials/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Дублировать материал
   */
  async duplicate(id) {
    const response = await api.post(`/materials/${id}/duplicate`)
    return response.data
  },

  /**
   * Получить QR-код для материала
   */
  async getQRCode(id) {
    const response = await api.get(`/materials/${id}/qrcode`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Массовое обновление статуса
   */
  async bulkUpdateStatus(ids, status, notes = '') {
    const response = await api.post('/materials/bulk-status', {
      material_ids: ids,
      status,
      notes
    })
    return response.data
  },

  /**
   * Поиск материалов по штрих-коду
   */
  async searchByBarcode(barcode) {
    const response = await api.get(`/materials/barcode/${barcode}`)
    return response.data
  },

  /**
   * Получить материалы, требующие внимания
   */
  async getRequiringAttention() {
    const response = await api.get('/materials/requiring-attention')
    return response.data
  },

  /**
   * Получить материалы в карантине
   */
  async getQuarantined() {
    const response = await api.get('/materials/quarantined')
    return response.data
  },

  /**
   * Получить материалы с истекающими сертификатами
   */
  async getExpiringCertificates(days = 30) {
    const response = await api.get(`/materials/expiring-certificates?days=${days}`)
    return response.data
  }
}