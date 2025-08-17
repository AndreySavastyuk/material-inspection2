import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const currentRole = ref(null)

  const isAuthenticated = computed(() => !!currentUser.value)

  function setRole(role) {
    currentRole.value = role
  }

  function logout() {
    currentUser.value = null
    currentRole.value = null
  }

  return {
    currentUser,
    currentRole,
    isAuthenticated,
    setRole,
    logout
  }
})