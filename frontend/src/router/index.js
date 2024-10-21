import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/shared/HomeView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: ['guest'] }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/shared/LoginView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: ['guest'] }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/shared/RegistrationView.vue'), // Lazy-loaded
      meta: { requiresAuth: false, type: ['guest'] }
    },
    {
      path: '/participant/activity/:id',
      name: 'Activity',
      component: () => import('@/views/ActivityDetailsView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['participant'] }
    },
    {
      path: '/organizer/activity/:id',
      name: 'OrganizerActivity',
      component: () => import('@/views/ActivityDetailsView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['organizer'] }
    },
    {
      path: '/reservations',
      name: 'Reservations',
      component: () => import('@/views/participant/ReservationsView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['participant'] }
    },
    {
      path: '/edit-profile/:username',
      name: 'EditProfile',
      component: () => import('@/views/shared/EditProfileView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['participant', 'organizer'] }
    },
    {
      path: '/subscriptions',
      name: 'Subscriptions',
      component: () => import('@/views/participant/SubscriptionsView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['participant'] }
    },
    {
      path: '/subscribers',
      name: 'Subscribers',
      component: () => import('@/views/organizer/SubscribersView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['organizer'] }
    },
    {
      path: '/participant/home',
      name: 'ParticipantHome',
      component: () => import('@/views/participant/ParticipantView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['participant'] }
    },
    {
      path: '/organizer/home',
      name: 'OrganizerHome',
      component: () => import('@/views/organizer/OrganizerView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['organizer'] }
    },
    {
      path: '/organizer/create-activity',
      name: 'CreateActivity',
      component: () => import('@/views/organizer/CreateActivityView.vue'), // Lazy-loaded
      meta: { requiresAuth: true, type: ['organizer'] }
    },
    {
      path: '/:catchAll(.*)',
      name: 'not-found',
      component: () => import('@/views/shared/NotFoundView.vue') // Lazy-loaded
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  if (!to.meta.requiresAuth) {
    if (userStore.isLoggedIn) {
      if (userStore.isParticipant) {
        next({ name: 'ParticipantHome' })
      } else if (userStore.isOrganizer) {
        next({ name: 'OrganizerHome' })
      }
    } else {
      next()
    }
  } else {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login' })
    } else {
      if (to.meta.type.includes(userStore.getType)) {
        next()
      } else {
        if (userStore.isParticipant) {
          next({ name: 'ParticipantHome' })
        } else if (userStore.isOrganizer) {
          next({ name: 'OrganizerHome' })
        }
      }
    }
  }
})
export default router
