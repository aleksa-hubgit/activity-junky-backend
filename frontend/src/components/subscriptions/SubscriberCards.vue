
<script setup>
import { defineProps } from 'vue';
import SubscriberCard from './SubscriberCard.vue';

const props = defineProps(
    {
        subscribers: {
            type: Array,
            required: true
        }
    }
);
</script>

<template>
    <div class="max-w-6xl mx-auto p-5">
      <h1 class="text-3xl font-bold mb-4 text-gray-800">Subscribers</h1>
      <p class="text-gray-600 mb-6">Total subscribers: {{ props.subscribers.length }}</p>
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="subscriber in props.subscribers"
          :key="subscriber.id"
          class="p-4 bg-white shadow-md rounded-lg"
        >
          <SubscriberCard :subscriber="subscriber" />
        </div>
      </div>
    </div>
  </template>
