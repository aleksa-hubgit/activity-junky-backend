import client from './client' 

const UserService = {
  getByUsername: async (username) => {
    try {
      const response = await client.get('/users/' + username)
      console.log(response.data)
      return response.data
    } catch (error) {
      console.error("Couldn't get user:", error)
      throw error
    }
  },

}

export default UserService