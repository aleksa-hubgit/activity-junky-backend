<script setup>
import SubscriptionService from '@/api-service/subscription-service';
import SubscriberCards from '@/components/subscriptions/SubscriberCards.vue';
import { useUserStore } from '@/stores/user';
import { onMounted, ref } from 'vue';

onMounted(() => {
    const userStore = useUserStore();
    SubscriptionService.getAllSubscribers(userStore.getUsername)
        .then(response => {
            subscribers.value = response;
            console.log(subscribers.value);
        })
        .catch(error => {
            console.error(error);
        });
});
const subscribers = ref([]);
</script>

<template>
    <SubscriberCards :subscribers="subscribers"/>
</template>