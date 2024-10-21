<script setup>
import { defineProps } from 'vue';
const props = defineProps(
    {
        subscriber: Object,
    }
);
</script>

<template>
    <div>
      <h2 class="text-xl font-semibold text-gray-800">User: {{ props.subscriber.participant }}</h2>
      <p class="text-gray-500">Date of subscription: {{ props.subscriber.date }}</p>
    </div>
  </template>