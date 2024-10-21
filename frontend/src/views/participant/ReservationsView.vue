<script setup>
import ReservationService from '@/api-service/reservation-service';
import ReservationCards from '@/components/reservations/ReservationCards.vue';
import { useUserStore } from '@/stores/user';
import { onMounted, ref } from 'vue';

const reservations = ref([]);
onMounted(()=> {
    const userStore = useUserStore();
    console.log('Reservations view mounted');
    const username = userStore.getUsername;
    ReservationService.getAllReservations(username)
        .then(res => {
            reservations.value = res;
        })
        .catch(error => {
            console.error(error);
        });
    }
);
</script>

<template>
    <ReservationCards :reservations="reservations" />
</template>