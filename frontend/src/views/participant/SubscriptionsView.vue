<script setup>
import SubscriptionService from '@/api-service/subscription-service';
import SubscriptionCards from '@/components/subscriptions/SubscriptionCards.vue';
import { useUserStore } from '@/stores/user';
import { onMounted, ref } from 'vue';

onMounted(() => {
    const userStore = useUserStore();
    SubscriptionService.getAllSubscriptions(userStore.getUsername)
        .then(response => {
            subscriptions.value = response;
        })
        .catch(error => {
            console.error(error);
        });
});
const subscriptions = ref([]);
</script>

<template>
    <SubscriptionCards :subscriptions="subscriptions"/>
</template>