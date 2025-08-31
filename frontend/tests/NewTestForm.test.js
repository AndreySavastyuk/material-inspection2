import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import NewTestForm from '@/components/NewTestForm.vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

// Mock services
vi.mock('@/services/testService', () => ({
  testService: {
    create: vi.fn()
  }
}))

vi.mock('@/services/materialService', () => ({
  materialService: {
    getAll: vi.fn().mockResolvedValue({
      items: [
        { id: '1', name: 'Сталь 09Г2С' },
        { id: '2', name: 'Алюминий АД31' }
      ]
    })
  }
}))

describe('NewTestForm', () => {
  let wrapper
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  const createWrapper = (props = {}) => {
    return mount(NewTestForm, {
      props: {
        visible: false,
        materialId: null,
        ...props
      },
      global: {
        plugins: [pinia, PrimeVue, ToastService],
        stubs: {
          Dialog: true,
          Button: true,
          Dropdown: true,
          InputNumber: true,
          Textarea: true
        }
      }
    })
  }

  describe('Инициализация', () => {
    it('должен корректно инициализироваться', () => {
      wrapper = createWrapper()
      expect(wrapper.exists()).toBe(true)
    })

    it('должен загружать список материалов при монтировании', async () => {
      wrapper = createWrapper()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.materials).toHaveLength(2)
      expect(wrapper.vm.materials[0].name).toBe('Сталь 09Г2С')
    })

    it('должен предустанавливать материал если передан materialId', () => {
      wrapper = createWrapper({ materialId: '1' })
      
      expect(wrapper.vm.form.materialId).toBe('1')
    })
  })

  describe('Типы и методы испытаний', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен содержать правильные типы испытаний', () => {
      const expectedTypes = [
        'mechanical',
        'chemical', 
        'non_destructive',
        'metallographic',
        'corrosion'
      ]
      
      const testTypeValues = wrapper.vm.testTypes.map(type => type.value)
      expectedTypes.forEach(type => {
        expect(testTypeValues).toContain(type)
      })
    })

    it('должен обновлять доступные методы при выборе типа', async () => {
      wrapper.vm.form.testType = 'mechanical'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.availableMethods.length).toBeGreaterThan(0)
      expect(wrapper.vm.availableMethods[0].value).toBe('tensile')
    })

    it('должен сбрасывать метод при смене типа испытания', async () => {
      wrapper.vm.form.testType = 'mechanical'
      wrapper.vm.form.testMethod = 'tensile'
      
      wrapper.vm.form.testType = 'chemical'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.form.testMethod).toBeNull()
    })
  })

  describe('Валидация формы', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен требовать выбор материала', () => {
      wrapper.vm.form.materialId = null
      wrapper.vm.form.testType = 'mechanical'
      
      const isValid = wrapper.vm.validateForm()
      
      expect(isValid).toBe(false)
      expect(wrapper.vm.errors.materialId).toBe('Выберите материал')
    })

    it('должен требовать выбор типа испытания', () => {
      wrapper.vm.form.materialId = '1'
      wrapper.vm.form.testType = null
      
      const isValid = wrapper.vm.validateForm()
      
      expect(isValid).toBe(false)
      expect(wrapper.vm.errors.testType).toBe('Выберите тип испытания')
    })

    it('должен проходить валидацию с корректными данными', () => {
      wrapper.vm.form.materialId = '1'
      wrapper.vm.form.testType = 'mechanical'
      
      const isValid = wrapper.vm.validateForm()
      
      expect(isValid).toBe(true)
      expect(Object.keys(wrapper.vm.errors).length).toBe(0)
    })
  })

  describe('Отправка формы', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен вызывать testService.create с правильными данными', async () => {
      const { testService } = await import('@/services/testService')
      testService.create.mockResolvedValue({ id: 'test_1' })
      
      wrapper.vm.form = {
        materialId: '1',
        testType: 'mechanical',
        testMethod: 'tensile',
        priority: 'medium',
        temperature: 20,
        sampleCount: 3,
        requirements: 'Тест требования',
        expectedStrength: 400,
        expectedElongation: 25,
        notes: 'Тестовые заметки'
      }
      
      await wrapper.vm.handleSubmit()
      
      expect(testService.create).toHaveBeenCalledWith({
        material_id: '1',
        test_type: 'mechanical',
        test_method: 'tensile',
        priority: 'medium',
        parameters: {
          temperature: 20,
          sample_count: 3,
          expected_strength: 400,
          expected_elongation: 25
        },
        requirements: 'Тест требования',
        notes: 'Тестовые заметки',
        status: 'planned',
        created_by: 'current_user'
      })
    })

    it('должен эмитить событие saved после успешной отправки', async () => {
      const { testService } = await import('@/services/testService')
      testService.create.mockResolvedValue({ id: 'test_1' })
      
      wrapper.vm.form.materialId = '1'
      wrapper.vm.form.testType = 'mechanical'
      
      await wrapper.vm.handleSubmit()
      
      expect(wrapper.emitted().saved).toBeTruthy()
    })

    it('не должен отправлять форму с невалидными данными', async () => {
      const { testService } = await import('@/services/testService')
      testService.create.mockClear()
      
      wrapper.vm.form.materialId = null
      
      await wrapper.vm.handleSubmit()
      
      expect(testService.create).not.toHaveBeenCalled()
    })
  })

  describe('Сброс формы', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен сбрасывать форму при отмене', () => {
      wrapper.vm.form.materialId = '1'
      wrapper.vm.form.testType = 'mechanical'
      wrapper.vm.form.notes = 'Test notes'
      wrapper.vm.errors.materialId = 'Some error'
      
      wrapper.vm.handleCancel()
      
      expect(wrapper.vm.form.materialId).toBeNull()
      expect(wrapper.vm.form.testType).toBeNull()
      expect(wrapper.vm.form.notes).toBe('')
      expect(Object.keys(wrapper.vm.errors).length).toBe(0)
    })

    it('должен сохранять предустановленный materialId при сбросе', () => {
      wrapper = createWrapper({ materialId: '1' })
      
      wrapper.vm.form.testType = 'mechanical'
      wrapper.vm.handleCancel()
      
      expect(wrapper.vm.form.materialId).toBe('1')
    })

    it('должен эмитить события при отмене', () => {
      wrapper.vm.handleCancel()
      
      expect(wrapper.emitted()['update:visible']).toBeTruthy()
      expect(wrapper.emitted().cancel).toBeTruthy()
    })
  })

  describe('Приоритеты', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен иметь правильные приоритеты', () => {
      const expectedPriorities = ['low', 'medium', 'high', 'critical']
      const actualPriorities = wrapper.vm.priorities.map(p => p.value)
      
      expectedPriorities.forEach(priority => {
        expect(actualPriorities).toContain(priority)
      })
    })

    it('должен устанавливать приоритет по умолчанию на medium', () => {
      expect(wrapper.vm.form.priority).toBe('medium')
    })
  })

  describe('Параметры по умолчанию', () => {
    beforeEach(() => {
      wrapper = createWrapper()
    })

    it('должен устанавливать правильные значения по умолчанию', () => {
      expect(wrapper.vm.form.temperature).toBe(20)
      expect(wrapper.vm.form.sampleCount).toBe(3)
      expect(wrapper.vm.form.priority).toBe('medium')
    })
  })
})