import client from './client' 

const ReservationService = {
  makeReservation: async (data) => {
    try {
      const response = await client.post('/reservations/', data)
      const reservation = response.data

      return reservation
    } catch (error) {
      console.error("Couldn't make reservation:", error)
      throw error
    }
  },

  cancelReservation: async (id) => {
    try {
      const response = await client.put('/reservations/cancel/'+id)
      return response.data
    } catch (error) {
      console.error("Couldn't cancel reservation:", error)
      throw error
    }
  },
  getAllReservations: async (username) => {
    try {
      const response = await client.get('/reservations/'+username)
      const reservations = response.data

      return reservations
    } catch (error) {
      console.error("Couldn't get reservations:", error)
      throw error
    }
  }

}

export default ReservationService
