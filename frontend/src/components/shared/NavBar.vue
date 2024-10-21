<script setup>
import { RouterLink, useRoute } from 'vue-router'
import logo from '@/assets/logo.png'
import { useUserStore } from '@/stores/user'
import router from '@/router'

const isActiveLink = (routePath) => {
  const route = useRoute()
  return route.path === routePath
}
const userStore = useUserStore()
const logout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<template>
  <nav class="border-b border-gray-800 bg-gray-800">
    <div class="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
      <div class="flex h-20 items-center justify-between">
        <div class="flex flex-1 items-center justify-center md:items-stretch md:justify-start">
          <RouterLink class="mr-4 flex flex-shrink-0 items-center" to="/">
            <img class="h-10 w-auto" :src="logo" alt="Vue Jobs" />
            <span class="ml-2 hidden text-2xl font-bold text-white md:block">Activity Junky</span>
          </RouterLink>
          <div class="md:ml-auto">
            <div class="flex space-x-2">
              <RouterLink
                to="/"
                :class="[
                  isActiveLink('/') ? 'bg-gray-800' : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Home</RouterLink
              >
              <RouterLink
                v-if="userStore.isLoggedIn && userStore.isOrganizer"
                to="/organizer/create-activity"
                :class="[
                  isActiveLink('/organizer/create-activity')
                    ? 'bg-gray-800'
                    : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Create Activity</RouterLink
              >
              <RouterLink
                v-if="userStore.isLoggedIn && userStore.isOrganizer"
                to="/subscribers"
                :class="[
                  isActiveLink('/organizer/create-activity')
                    ? 'bg-gray-800'
                    : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Subscribers</RouterLink
              >
              <RouterLink
                v-if="userStore.isLoggedIn && userStore.isParticipant"
                to="/reservations"
                :class="[
                  isActiveLink('/reservations')
                    ? 'bg-gray-800'
                    : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Reservations</RouterLink
              >
              <RouterLink
                v-if="userStore.isLoggedIn && userStore.isParticipant"
                to="/subscriptions"
                :class="[
                  isActiveLink('/participant/reservations')
                    ? 'bg-gray-800'
                    : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Subscriptions</RouterLink
              >
              <RouterLink
                v-if="userStore.isLoggedIn"
                :to="`/edit-profile/${userStore.getUsername}`"
                :class="[
                  isActiveLink(`/edit-profile/${userStore.getUsername}`)
                    ? 'bg-gray-800'
                    : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Profile</RouterLink
              >
              <RouterLink
                v-if="!userStore.isLoggedIn"
                to="/register"
                :class="[
                  isActiveLink('/register') ? 'bg-gray-800' : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Sign up</RouterLink
              >
              <RouterLink
                v-if="!userStore.isLoggedIn"
                to="/login"
                :class="[
                  isActiveLink('/login') ? 'bg-gray-800' : 'hover:bg-gray-700 hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
                >Sign in</RouterLink
              >
              <button
                v-if="userStore.isLoggedIn"
                @click="logout"
                :class="[
                  'hover:bg-gray-700',
                  'hover:text-white',
                  'text-white',
                  'px-3',
                  'py-2',
                  'rounded-md'
                ]"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
