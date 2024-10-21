<script setup>
import { useUserStore } from '@/stores/user';
import { ref } from 'vue';
import { computed, defineProps } from 'vue';
const props = defineProps(
    {
        user: Object,
    }
);
const isEditing = ref(false);
const editableUser = ref(
    props.user
)

const isOrganizer =computed(() => {
    return props.user.type === 'organizer';
});

const subscribe = () => {
    // TODO: Implement
    console.log('Subscribing');
};
const enableEditing = () => {
    isEditing.value = true
}

const userStore = useUserStore();

const cancelEditing = () => {
    isEditing.value = false
    editableUser.value = props.user
}

const saveChanges = () => {
    // need to implement a send to the backend server for the saving of userdata
}
</script>

<template>
    <div class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-sm">
            <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
                Profile details
            </h2>
        <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form class="space-y-6" action="#" method="POST" @submit.prevent="saveChanges">
                <div>
                    <label for="email" class="block text-sm font-medium leading-6 text-gray-900">
                        Email
                    </label>
                    <div class="mt-2">
                        <input
                        id="email"
                        v-model="editableUser.email"
                        name="email"
                        type="email"
                        autocomplete="email"
                        required="true"
                        disabled
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                        />
                    </div>
                </div>
                <div>
                    <label for="username" class="block text-sm font-medium leading-6 text-gray-900">
                        Username
                    </label>
                    <div class="mt-2">
                        <input
                        id="username"
                        v-model="editableUser.username"
                        name="username"
                        type="text"
                        autocomplete="text"
                        required="true"
                        disabled
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                        />
                    </div>
                </div>
                <div v-if="!isEditing">
                    <button @click.prevent="enableEditing" v-if="editableUser.username === userStore.getUsername" class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                        Subscribe
                    </button>
                </div>
                <div v-else class="flex space-x-4">
                    <button type="submit" class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                        Save changes
                    </button>
                    <button class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" @click.prevent="cancelEditing">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
        </div>
    <button @click.prevent="subscribe" v-if="userStore.isParticipant && isOrganizer">
      Subscribe
    </button>
    
    </div>
</template>
