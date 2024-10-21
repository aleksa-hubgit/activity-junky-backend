import client from './client' 

const SubscriptionService = {
  getAllSubscriptions: async (username) => {
    try {
      const response = await client.get('/subscriptions/'+ username)
      const reservation = response.data

      return reservation
    } catch (error) {
      console.error("Couldn't get subscriptions:", error)
      throw error
    }
  },

  getAllSubscribers: async (username) => {
    try {
      const response = await client.get('/subscriptions/subscribers/'+ username)
      return response.data
    } catch (error) {
      console.error("Couldn't get subscribers:", error)
      throw error
    }
  },
  subscribe: async (organizer, username) => {
    try {
      const response = await client.post(`/subscriptions/subscribe/${organizer}/${username}`)
      return response.data
    } catch (error) {
      console.error("Couldn't cancel reservation:", error)
      throw error
    }
  },
  unsubscribe: async (organizer, username) => {
    try {
      const response = await client.post(`/subscriptions/cancel/${organizer}/${username}`)
      return response.data
    } catch (error) {
      console.error("Couldn't cancel reservation:", error)
      throw error
    }
  },

}

export default SubscriptionService
