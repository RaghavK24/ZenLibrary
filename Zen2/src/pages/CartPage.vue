<template>
  <main-layout>
    <h2 class="text-center">Your Cart</h2>
    <div class="row col-md-8 col-lg-10 m-auto">
      <div class="my-1">
        <cart-component></cart-component>
      </div>
      <div class="col-md-8 col-lg-10 d-inline-flex justify-content-end m-auto mt-2 g-2">
        <button type="button" class="btn btn-sm btn-secondary mx-2" @click="router.push('/')">
          <mdicon name="home" :height="20" />Go to Home
        </button>
        <button
          type="button"
          class="btn btn-sm btn-primary ml-auto"
          :disabled="itemsLength === 0"
          @click="router.push('/checkout')"
        >

          <mdicon name="book-arrow-right" :height="20" />
          Send Requests
        </button>
      </div>
    </div>
  </main-layout>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { userequestStore } from '@/stores/cartstore.js'
import MainLayout from '@/layouts/MainLayout.vue'
import CartComponent from '@/components/CartComponent.vue'
import axiosClient from '@/js/axios.js'

const router = useRouter()


let itemsLength = 0; // Define a variable to store the length of items

async function fetchRequests() {
  try {
    console.log('Fetching requests...');
    const response = await axiosClient.get(`/api/request`);
    const items = response.data;
    console.log(response.data);
    localStorage.setItem('request', JSON.stringify(items));
    itemsLength = items.length; // Store the length of items
    return items; // Return the fetched items
  } catch (error) {
    console.error('Error fetching requests:', error);
    throw error; // Throw the error to be handled by the caller
  }
}

// Call fetchRequests to fetch the items and store the length of items
fetchRequests().catch(error => {
  console.error('Error:', error);
});
</script>

<style scoped>
th {
  vertical-align: middle;
  border-bottom: 3px solid #485460;
  font-size: 12px, bold;
}
</style>
