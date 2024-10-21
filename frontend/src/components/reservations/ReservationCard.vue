<script setup>
import ReservationService from '@/api-service/reservation-service';
import { defineProps } from 'vue';

const props = defineProps(
    {
        reservation: Object,
    }
);
const cancel = () => {
    console.log('Cancel reservation');
    ReservationService.cancelReservation(props.reservation.id)
        .then(() => {
            console.log('Reservation cancelled');
        })
        .catch(error => {
            console.error(error);
        });
};
</script>


<template>
    <div class="p-6 bg-white shadow-lg rounded-lg">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">Reservation</h2>
      <div class="text-gray-600 mb-2">
        <p class="mb-1"><span class="font-semibold">Date:</span> {{ props.reservation.date }}</p>
        <p class="mb-1"><span class="font-semibold">Organizer:</span> {{ props.reservation.organizer }}</p>
        <p class="mb-1"><span class="font-semibold">Activity:</span> {{ props.reservation.activity_name }}</p>
        <p class="mb-1"><span class="font-semibold">Price:</span> ${{ props.reservation.price }}</p>
        <p class="mb-1"><span class="font-semibold">Category:</span> {{ props.reservation.category }}</p>
      </div>
      <button
        class="mt-4 px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400"
        @click.prevent="cancel"
      >
        Cancel
      </button>
    </div>
  </template>