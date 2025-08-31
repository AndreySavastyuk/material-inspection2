import api from './api'

export const testService = {
  /**
   * Получить список всех результатов испытаний
   */
  async getAll(filters = {}) {
    const params = new URLSearchParams()

    if (filters.search) params.append('search', filters.search)
    if (filters.testTypes?.length) {
      filters.testTypes.forEach(type => params.append('test_type', type))
    }
    if (filters.category) params.append('category', filters.category)
    if (filters.result) params.append('result', filters.result)
    if (filters.tester) params.append('tester_id', filters.tester)

    if (filters.dateRange) {
      if (filters.dateRange[0]) {
        params.append('date_from', filters.dateRange[0].toISOString())
      }
      if (filters.dateRange[1]) {
        params.append('date_to', filters.dateRange[1].toISOString())
      }
    }

    const response = await api.get(`/tests?${params.toString()}`)
    return response.data
  },

  /**
   * Получить результаты испытаний для материала
   */
  async getByMaterialId(materialId) {
    const response = await api.get(`/materials/${materialId}/tests`)
    return response.data
  },

  /**
   * Получить детали испытания
   */
  async getById(id) {
    const response = await api.get(`/tests/${id}`)
    return response.data
  },

  /**
   * Создать новое испытание
   */
  async create(data) {
    const testData = {
      material_id: data.material_id,
      test_type: data.test_type,
      test_category: data.test_category,
      scheduled_date: data.scheduled_date,
      priority: data.priority || 'normal',
      notes: data.notes,
      required_standards: data.required_standards || [],
      assigned_to: data.assigned_to
    }

    const response = await api.post('/tests', testData)
    return response.data
  },

  /**
   * Обновить результаты испытания
   */
  async updateResults(id, results) {
    const response = await api.put(`/tests/${id}/results`, {
      pass_fail: results.pass_fail,
      numeric_results: results.numeric_results,
      text_results: results.text_results,
      images: results.images,
      notes: results.notes,
      tested_at: results.tested_at || new Date().toISOString(),
      equipment_used: results.equipment_used,
      test_conditions: results.test_conditions
    })
    return response.data
  },

  /**
   * Загрузить изображения для испытания
   */
  async uploadImages(id, files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('images', file)
    })

    const response = await api.post(`/tests/${id}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },

  /**
   * Удалить испытание
   */
  async delete(id) {
    const response = await api.delete(`/tests/${id}`)
    return response.data
  },

  /**
   * Генерировать отчет по испытанию
   */
  async generateReport(id) {
    const response = await api.get(`/tests/${id}/report`, {
      responseType: 'blob'
    })

    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `test_report_${id}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Генерировать массовый отчет
   */
  async generateBulkReport(ids) {
    const response = await api.post('/tests/bulk-report', {
      test_ids: ids
    }, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `bulk_test_report_${new Date().toISOString().split('T')[0]}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Экспортировать в Excel
   */
  async exportToExcel(ids = null) {
    const params = ids ? { test_ids: ids } : {}

    const response = await api.post('/tests/export', params, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `tests_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Экспортировать полный отчет
   */
  async exportFullReport(filters = {}) {
    const params = new URLSearchParams()

    if (filters.dateRange) {
      if (filters.dateRange[0]) {
        params.append('date_from', filters.dateRange[0].toISOString())
      }
      if (filters.dateRange[1]) {
        params.append('date_to', filters.dateRange[1].toISOString())
      }
    }

    const response = await api.get(`/tests/full-report?${params.toString()}`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `full_test_report_${new Date().toISOString().split('T')[0]}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Создать повторное испытание
   */
  async createRetest(materialId, testType) {
    const response = await api.post('/tests/retest', {
      material_id: materialId,
      test_type: testType,
      reason: 'Previous test failed'
    })
    return response.data
  },

  /**
   * Получить счетчики для dashboard
   */
  async getCounters() {
    const response = await api.get('/tests/counters')
    return response.data
  },

  /**
   * Получить статистику испытаний
   */
  async getStatistics(period = 'month') {
    const response = await api.get(`/tests/statistics?period=${period}`)
    return response.data
  },

  /**
   * Получить историю испытаний материала
   */
  async getMaterialTestHistory(materialId) {
    const response = await api.get(`/materials/${materialId}/test-history`)
    return response.data
  },

  /**
   * Проверить соответствие стандартам
   */
  async checkCompliance(testId) {
    const response = await api.post(`/tests/${testId}/check-compliance`)
    return response.data
  },

  /**
   * Получить список оборудования для испытаний
   */
  async getEquipment() {
    const response = await api.get('/tests/equipment')
    return response.data
  },

  /**
   * Получить стандарты для типа испытания
   */
  async getStandards(testType) {
    const response = await api.get(`/tests/standards/${testType}`)
    return response.data
  },

  /**
   * Скачать протокол испытания
   */
  async downloadReport(testId) {
    const response = await api.get(`/tests/${testId}/protocol`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `protocol_${testId}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()

    return response.data
  },

  /**
   * Утвердить результаты испытания
   */
  async approve(testId, approvalData) {
    const response = await api.post(`/tests/${testId}/approve`, {
      approved_by: approvalData.approved_by,
      approval_notes: approvalData.notes,
      digital_signature: approvalData.signature
    })
    return response.data
  },

  /**
   * Отклонить результаты испытания
   */
  async reject(testId, rejectionData) {
    const response = await api.post(`/tests/${testId}/reject`, {
      rejected_by: rejectionData.rejected_by,
      rejection_reason: rejectionData.reason,
      requires_retest: rejectionData.requires_retest
    })
    return response.data
  },

  /**
   * Получить шаблон протокола
   */
  async getProtocolTemplate(testType) {
    const response = await api.get(`/tests/protocol-template/${testType}`)
    return response.data
  },

  /**
   * Сохранить шаблон протокола
   */
  async saveProtocolTemplate(testType, template) {
    const response = await api.post(`/tests/protocol-template/${testType}`, template)
    return response.data
  },

  /**
   * Добавить результаты к испытанию
   * @param {string} testId - ID испытания
   * @param {Object} resultsData - Данные результатов
   * @returns {Promise} - Результаты испытания
   */
  async addResults(testId, resultsData) {
    const response = await api.post(`/tests/${testId}/results`, resultsData)
    return response.data
  },

  /**
   * Обновить статус испытания
   * @param {string} id - ID испытания
   * @param {string} status - Новый статус
   * @param {string} comment - Комментарий к изменению
   * @returns {Promise} - Обновленное испытание
   */
  async updateStatus(id, status, comment = '') {
    const response = await api.patch(`/tests/${id}/status`, {
      status,
      comment
    })
    return response.data
  },

  /**
   * Получить все планируемые тесты
   */
  async getPlanned(params = {}) {
    const response = await api.get('/tests/planned', { params })
    return response.data
  },

  /**
   * Получить активные тесты
   */
  async getActive(params = {}) {
    const response = await api.get('/tests/active', { params })
    return response.data
  },

  /**
   * Получить завершенные тесты
   */
  async getCompleted(params = {}) {
    const response = await api.get('/tests/completed', { params })
    return response.data
  }
}