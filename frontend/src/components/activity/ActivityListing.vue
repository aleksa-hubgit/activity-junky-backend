<script setup>
import { RouterLink } from 'vue-router';
import { computed, defineProps } from 'vue';
import ReservationService from '@/api-service/reservation-service';
import { useUserStore } from '@/stores/user';
import ActivityService from '@/api-service/activity-service';
import SubscriptionService from '@/api-service/subscription-service';

const props = defineProps({
  activity: Object,
  type: String,
});
const isAvailable = computed(() => {
  return props.activity.total_places > 0;
}); ;
const isParticipant = computed(() => {
  return props.type === 'participant';
});
const isOrganizer = computed(() => {
  return props.type === 'organizer';
});

const makeReservation = () => {
  console.log('Making reservation');
  ReservationService.makeReservation({ activity_id: props.activity.id, participant_username: useUserStore().getUsername })
    .then((response) => {
      console.log('Reservation made', response);
    })
    .catch((error) => {
      console.error('Error making reservation', error);
    });
};

const cancelActivity = () => {
  ActivityService.cancel(props.activity.id)
    .then((response) => {
      console.log('Activity cancelled', response);
    })
    .catch((error) => {
      console.error('Error cancelling activity', error);
    });
}

const showReservations = () => {
  console.log('Showing reservations');
}

const subscribe = () => {
  const userStore = useUserStore();
  SubscriptionService.subscribe(props.activity.username, userStore.getUsername)
    .then((response) => {
      console.log('Subscribed', response);
    })
    .catch((error) => {
      console.error('Error subscribing', error);
    });
}

</script>

<template>
  <div class="bg-white rounded-xl shadow-md relative">
    <div class="p-4">
      <div class="mb-6">
        <div class="text-gray-600 my-2">{{ activity.category.toUpperCase() }}</div>
        <h3 class="text-xl font-bold">{{ activity.name }}</h3>
        <div v-if="isParticipant">
          <h3 class="text-gray-800 mb-2">By: {{ activity.username }}</h3>
          <button
            class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
            @click.prevent="subscribe">
            Subscribe
          </button>
        </div>
        
      </div>

      <div class="mb-5">
        <div>
          {{ props.activity.description }}
        </div>
      </div>

      <h3 class="text-gray-800 mb-2">Price: ${{ activity.price }}</h3>
      <h3 class="text-gray-800 mb-2">Places left: {{ activity.total_places }}</h3>

      <div class="border border-gray-100 mb-5"></div>

      <div class="flex flex-col lg:flex-row justify-between mb-4">
        <div class="text-orange-800 mb-3">
          {{ activity.date }}
        </div>
        <RouterLink
          v-if = "isParticipant || isOrganizer"
          :to="'/' + type + '/activity/' + activity.id"
          class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
        >
          Details
        </RouterLink>
        <button
          class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
          v-if="isOrganizer"
          @click.prevent="cancelActivity"
          >
          Cancel
        </button>
        <button
          class="h-[36px] bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-center text-md font-semibold"
          v-if="isOrganizer"
          @click.prevent="showReservations"
          >
          Reservations
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
  </div>
</template>