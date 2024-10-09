<script setup>
import { RouterLink } from 'vue-router';
import { defineProps } from 'vue';

const props = defineProps({
  activity: Object,
  type: String,
});

</script>

<template>
  <div class="bg-white rounded-xl shadow-md relative">
    <div class="p-4">
      <div class="mb-6">
        <div class="text-gray-600 my-2">Category: {{ activity.category }}</div>
        <h3 class="text-xl font-bold">{{ activity.name }}</h3>
      </div>

      <div class="mb-5">
        <div>
          {{ props.activity.description }}
        </div>
      </div>

      <h3 class="text-gray-800 mb-2">Price: {{ activity.price }}</h3>
      <h3 class="text-gray-800 mb-2">Total places: {{ activity.total_places }}</h3>

      <div class="border border-gray-100 mb-5"></div>

      <div class="flex flex-col lg:flex-row justify-between mb-4">
        <div class="text-orange-700 mb-3">
          <i class="pi pi-map-marker text-orange-700"></i>
          {{ activity.date }}
        </div>
        <RouterLink
          :to="'/' + type + '/activity/' + activity.id"
          class="h-[36px] bg-white hover:bg-gray-200 text-black px-4 py-2 rounded-lg text-center text-md"
        >
          Details
        </RouterLink>
        <button
          class="h-[36px] bg-white hover:bg-gray-200 text-black px-4 py-2 rounded-lg text-center text-md"
          v-if="type === 'organizer'"
          >
          Cancel
        </button>
        <button
          class="h-[36px] bg-white hover:bg-gray-200 text-black px-4 py-2 rounded-lg text-center text-md"
          v-else-if="type === 'participant'"
          >
          Make reservation
        </button>
      </div>
    </div>
  </div>
</template>