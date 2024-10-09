import client from './client' // Import your Axios client

const ActivityService = {
  getAll: async (query) => {
    try {
      const response = await client.get('/activities', {
        params: query || {} // Use Axios's params option to handle query parameters
      })
      const activities = response.data
      return activities
    } catch (error) {
      console.error('Get all failed:', error)
      throw error
    }
  },
  create: async (activity) => {
    try {
      const response = await client.post('/activities', activity)
      const createdActivity = response.data
      return createdActivity
    } catch (error) {
      console.error('Create failed:', error)
      throw error
    }
  },
}

export default ActivityService
