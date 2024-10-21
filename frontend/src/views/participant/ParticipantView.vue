<script setup>
import ActivityService from '@/api-service/activity-service';
import ActivityListings from '@/components/activity/ActivityListings.vue'
import { useUserStore } from '@/stores/user';
import { onMounted, reactive } from 'vue';
const state = reactive({
  activities: [],
  isLoading: true,
})
const userStore = useUserStore()
onMounted(async () => {
  ActivityService.getAll({ })
    .then((response) => {
      state.activities = response
    })
    .catch((error) => {
      console.error('Error fetching activities', error)
      state.isLoading = false
    })
    .finally(() => {
      state.isLoading = false
    })
})
</script>

<template>
  <ActivityListings v-if="state.activities.length > 0 && !state.isLoading" :activities="state.activities" :type="userStore.getType"/>
  <div
    v-else-if="!state.activities.length > 0 && !state.isLoading"
    class="flex h-96 items-center justify-center"
  >
    <p class="text-2xl">
      No activities found
    </p> 
  </div>
  <div v-else-if="state.isLoading" class="flex h-96 items-center justify-center">
    <p class="text-2xl">Loading...</p>
  </div>
</template>
