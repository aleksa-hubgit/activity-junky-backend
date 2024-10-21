<script setup>
import { defineProps } from 'vue';
import ReservationCard from '@/components/reservations/ReservationCard.vue';

const props = defineProps(
    {
        reservations: Array,
    }
);
</script>

<template>
    <div class="max-w-full md:max-w-5xl mx-auto px-4 md:px-6 py-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="reservation in props.reservations" :key="reservation.id">
          <ReservationCard :reservation="reservation" />
        </div>
      </div>
    </div>
  </template>