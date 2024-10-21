<script setup>
import SubscriptionService from '@/api-service/subscription-service';
import { defineProps } from 'vue';
const props = defineProps(
    {
        subscription: Object,
    }
);
const unsubscribe = () => {
    SubscriptionService.unsubscribe(props.subscription.organizer, props.subscription.participant)
        .then(() => {
            console.log('Unsubscribed');
        })
        .catch(error => {
            console.error(error);
        });
};
</script>

<template>
    <div>
      <h2 class="text-xl font-semibold text-gray-800">User: {{ props.subscription.organizer }}</h2>
      <p class="text-gray-500">{{ props.subscription.date }}</p>
      <button
        @click.prevent="unsubscribe"
        class="mt-4 px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-red-400"
      >
        Unsubscribe
      </button>
    </div>
  </template>