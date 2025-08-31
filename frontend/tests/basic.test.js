import { describe, it, expect } from 'vitest'

describe('Basic Tests', () => {
  it('должен выполняться простой тест', () => {
    expect(1 + 1).toBe(2)
  })

  it('должен проверять строки', () => {
    expect('hello world').toContain('world')
  })

  it('должен проверять массивы', () => {
    const testArray = [1, 2, 3, 4, 5]
    expect(testArray).toHaveLength(5)
    expect(testArray).toContain(3)
  })

  it('должен проверять объекты', () => {
    const testObject = { 
      name: 'Test', 
      value: 42, 
      active: true 
    }
    
    expect(testObject).toHaveProperty('name', 'Test')
    expect(testObject.value).toBeGreaterThan(40)
    expect(testObject.active).toBe(true)
  })
})