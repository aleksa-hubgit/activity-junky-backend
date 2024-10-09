import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: 'guest' }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: 'guest' }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/RegistrationView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: 'guest' }
    },
    {
      path: '/participant/home',
      name: 'ParticipantHome',
      component: () => import('@/views/ParticipantView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: 'participant' }
    },
    {
      path: '/organizer/home',
      name: 'OrganizerHome',
      component: () => import('@/views/OrganizerView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: 'organizer' }
    },
    {
      path: '/organizer/create-activity',
      name: 'CreateActivity',
      component: () => import('@/views/CreateActivityView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: 'organizer' }
    },
    {
      path: '/:catchAll(.*)',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue') // Lazy-loaded
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  console.log('Requires auth:', to.meta.requiresAuth)
  if (!to.meta.requiresAuth) {
    if (userStore.isLoggedIn) {
      if (userStore.getType === 'participant') {
        next({ name: 'ParticipantHome' })
      } else if (userStore.getType === 'organizer') {
        next({ name: 'OrganizerHome' })
      }
    } else {
      next()
    }
  } else {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login' })
    } else {
      console.log('User type:', userStore.getType)
      if (userStore.getType === to.meta.type) {
        next()
      } else {
        console.log('User type:', userStore.getType)
        if (userStore.getType === 'participant') {
          next({ name: 'ParticipantHome' })
        } else if (userStore.getType === 'organizer') {
          next({ name: 'OrganizerHome' })
        }
      }
    }
  }
})
export default router
