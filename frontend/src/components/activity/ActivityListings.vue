<script setup>
import {  defineProps } from 'vue'
import ActivityListing from '@/components/activity/ActivityListing.vue'

defineProps({
  activities: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: ''
  }
})

</script>

<template>
  <section class="bg-white px-4 py-10">
    <div class="container-xl m-auto lg:container">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2" v-if="activities.length > 0">
        <ActivityListing
          v-for="activity in activities.slice(0, activities.length)"
          :key="activity.id"
          :activity="activity"
          :type="type"
        />
      </div>
      <div v-else class="flex h-96 items-center justify-center">
        <p class="text-2xl">
          No activities found
        </p>
      </div>
    </div>
    
  </section>
</template>
