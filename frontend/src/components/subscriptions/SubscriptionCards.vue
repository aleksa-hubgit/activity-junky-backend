
<script setup>
import { defineProps } from 'vue';
import SubscriptionCard from './SubscriptionCard.vue';
const props = defineProps(
    {
        subscriptions: {
        type: Array,
        required: true
        }
    }  
);

</script>

<template>
  <div class="max-w-6xl mx-auto p-5">
    <h1 class="text-3xl font-bold mb-4 text-gray-800">Subscriptions</h1>
    <p class="text-gray-600 mb-6">Total subscriptions: {{ props.subscriptions.length }}</p>
    <div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="subscription in props.subscriptions"
        :key="subscription.id"
        class="p-4 bg-white shadow-md rounded-lg"
      >
        <SubscriptionCard :subscription="subscription" />
      </div>
    </div>
  </div>
</template>