// services/authService.js
import client from './client' // Import your Axios client
import { useUserStore } from '@/stores/user'

const AuthService = {
  login: async (data) => {
    try {
      const response = await client.post('/auth/login', data)
      const user = response.data.login_response
      const userStore = useUserStore()
      userStore.setUser(user)

      return user
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  },

  register: async (data) => {
    console.log('data', data)
    try {
      const response = await client.post('/auth/register', data)
      return response.data
    } catch (error) {
      console.error('Registration failed:', error)
      throw error
    }
  },

  logout: () => {
    try {
      const userStore = useUserStore()
      userStore.logout()

      return true
    } catch (error) {
      console.error('Logout failed:', error)
      throw error
    }
  }
}

export default AuthService
