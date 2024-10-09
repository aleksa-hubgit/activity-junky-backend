<script setup>
import {  defineProps } from 'vue'
import ActivityListing from '@/components/ActivityListing.vue'

defineProps({
  limit: Number,
  showButton: {
    type: Boolean,
    default: false
  },
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
      <div class="grid grid-cols-1 gap-6 md:grid-cols-3" v-if="activities.length > 0">
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

  <section v-if="showButton" class="m-auto my-10 max-w-lg px-6">
  </section>
</template>
