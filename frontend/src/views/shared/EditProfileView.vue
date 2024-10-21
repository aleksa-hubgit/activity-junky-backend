<script setup>
import EditProfileForm from '@/components/shared/EditProfileForm.vue';
import { useUserStore } from '@/stores/user';
import { onMounted, reactive } from 'vue';
const state = reactive({
  user: null,
  isLoading: true,
})
onMounted(() => {
  const userStore = useUserStore()
  state.user = userStore.getUser
  state.isLoading = false
});
</script>

<template>
    <div v-if="state.isLoading">
        <p>Loading...</p>
    </div>
    <div v-else-if="!state.isLoading && state.user">
        <EditProfileForm :user="state.user" />
    </div>
    <div v-else>
        <p>User not found</p>
    </div>
</template>