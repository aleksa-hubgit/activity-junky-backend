<script setup>
import { useRoute } from 'vue-router';
import { computed, onMounted, reactive } from 'vue';
import ReservationService from '@/api-service/reservation-service';
import ActivityService from '@/api-service/activity-service';
import { useUserStore } from '@/stores/user';

const state = reactive({
  activity: {},
  isLoading: true,
  type: useUserStore().getType,
});
const isAvailable = computed(() => {
  return state.activity.total_places > 0;
}); ;
const isParticipant = computed(() => {
  return state.type === 'participant';
});
const isOrganizer = computed(() => {
  return state.type === 'organizer';
});


const makeReservation = () => {
    console.log('Making reservation');
    console.log('Activity:', state.activity);
    console.log({activity_id: state.activity.id, participant_username: useUserStore().getUsername});
  ReservationService.makeReservation({ activity_id: state.activity.id, participant_username: useUserStore().getUsername })
    .then((response) => {
      console.log('Reservation made', response);
    })
    .catch((error) => {
      console.error('Error making reservation', error);
    });
};

const cancel = () => {
  console.log('Cancelling activity');
  ActivityService.cancel(state.activity.id)
    .then((response) => {
      console.log('Activity cancelled', response);
    })
    .catch((error) => {
      console.error('Error cancelling activity', error);
    });
}

onMounted(async () => {
  const id = useRoute().params.id
  ActivityService.get(id)
    .then((response) => {
      console.log('Response:', response)
      state.activity = response
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
    <div class="p-4" v-if="!state.isLoading && state.activity">
    <div class="mb-6">
        <div class="text-gray-600 my-2">Category: {{ state.activity.category.toUpperCase() }}</div>
        <h3 class="text-xl font-bold">{{ state.activity.name }}</h3>
        <h3 class="text-gray-800 mb-2">Organizer: {{ state.activity.username }}</h3>
        <h3 class="text-gray-800 mb-2">Status: {{ state.activity.status }}</h3>
    </div>

    <div class="mb-5">
        <div>
        {{ state.activity.description }}
        </div>
    </div>

    <h3 class="text-gray-800 mb-2">Price: {{ state.activity.price }}</h3>
    <h3 class="text-gray-800 mb-2">Total places: {{ state.activity.total_places }}</h3>

    <div class="border border-gray-100 mb-5"></div>

    <div class="flex flex-col lg:flex-row justify-between mb-4">
        <div class="text-orange-700 mb-3">
        <i class="pi pi-map-marker text-orange-700"></i>
        {{ state.activity.date }}
        </div>
        <button
        class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
        v-if="isOrganizer"
        @click.prevent="cancel"
        >
        Cancel
        </button>
        <button
        class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
        v-else-if="isParticipant && isAvailable"
        @click.prevent="makeReservation"
        >
        Make reservation
        </button>
    </div>
    </div>
  
    <div v-else-if="state.isLoading">
      <p>Loading...</p> <!-- Show loading message when data is being fetched -->
    </div>
  
    <div v-else>
      <p>No activity found.</p> <!-- Show message if no activity is found -->
    </div>
  </template>