import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = computed(() => user.value?.token)
  const getUser = computed(() => user.value)
  const isLoggedIn = computed(() => !!user.value)
  const getType = computed(() => user.value?.user_type)
  const getUsername = computed(() => user.value?.username)
  const isOrganizer = computed(() => user.value?.user_type === 'organizer')
  const isParticipant = computed(() => user.value?.user_type === 'participant')

  function setUser(newUser) {
    user.value = newUser
  }
  function logout() {
    user.value = null
  }

  return {
    user,
    token,
    setUser,
    logout,
    getUser,
    isLoggedIn,
    getType,
    getUsername,
    isOrganizer,
    isParticipant
  }
})
