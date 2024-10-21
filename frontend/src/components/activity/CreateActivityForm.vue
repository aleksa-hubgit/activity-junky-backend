<script setup>
import router from '@/router'
import ActivityService from '@/api-service/activity-service';
import { ref } from 'vue'
import { useUserStore } from '@/stores/user';
const name = ref('')
const description = ref('')
const date = ref("")
const price = ref(0)
const total_places = ref(0)
const status = ref('available')
const userStore = useUserStore()
const category = ref('Sport')
const create = () => {
  ActivityService.create({
    name: name.value,
    description: description.value,
    date: date.value,
    price: price.value,
    total_places: total_places.value,
    status: status.value,
    category: category.value.toLowerCase(),
    username: userStore.getUsername
  })
    .then((response) => {
      console.log('Response:', response)
      router.push({ name: 'Login' })
    })
    .catch((error) => {
      console.log('Error:', error)
    })
}
</script>
<template>
  <div class="flex min-h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-sm">
      <img
        class="mx-auto h-10 w-auto"
        src="https://tailwindui.com/plus/img/logos/mark.svg?color=indigo&shade=600"
        alt="Your Company"
      />
      <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
        Create activity
      </h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <form class="space-y-6" action="#" method="POST" @submit.prevent="create">
        <div>
          <label for="name" class="block text-sm font-medium leading-6 text-gray-900">Name</label>
          <div class="mt-2">
            <input
              id="name"
              v-model="name"
              name="name"
              type="text"
              required="true"
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>
        <div>
          <label for="description" class="block text-sm font-medium leading-6 text-gray-900"
            >Description</label
          >
          <div class="mt-2">
            <textarea
              id="description"
              v-model="description"
              name="description"
              autocomplete="off"
              required
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between">
            <label for="date" class="block text-sm font-medium leading-6 text-gray-900"
              >Date</label
            >
          </div>
          <div class="mt-2">
            <input
              id="date"
              v-model="date"
              name="date"
              type="text"
              autocomplete="off"
              required
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>
        <div>
          <div class="flex items-center justify-between">
            <label for="total-places" class="block text-sm font-medium leading-6 text-gray-900"
              >Total places</label
            >
          </div>
          <div class="mt-2">
            <input
              id="total-places"
              v-model="total_places"
              name="total-places"
              type="number"
              step="1"
              min="0"
              required
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>
        <div>
          <div class="flex items-center justify-between">
            <label for="price" class="block text-sm font-medium leading-6 text-gray-900"
              >Price</label
            >
          </div>
          <div class="mt-2">
            <input
              id="price"
              v-model="price"
              name="price"
              type="number"
              step="0.1"
              min="0"
              required
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            />
          </div>
        </div>
        <div>
          <label for="category" class="block text-sm font-medium leading-6 text-gray-900"
            >Category</label
          >
          <div class="relative mt-2">
            <select
              id="category"
              v-model="category"
              class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            >
              <option>Sport</option>
              <option>Art</option>
              <option>Education</option>
            </select>
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
          >
            Create
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
