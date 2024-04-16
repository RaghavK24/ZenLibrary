<template>
  <!-- <h2 class="text-center">Your Cart</h2> -->
  <div class="card card-body col-md-8 col-lg-10 m-auto p-0">
    <div class="row col-12 justify-content-center m-auto p-0">
      <div v-if="cart.items.length > 0" class="mt-3">
        <table class="table table-responsive table-nowrap text-center">
          <thead class="border-bottom table-light">
            <tr>
              <th scope="col"><b>#</b></th>
              <th scope="col"><b>ITEM</b></th>
              <th scope="col"><b>AUTHOR</b></th>
              <th scope="col"><b>SECTION</b></th>
              <th scope="col"><b>STATUS</b></th>             
              <th scope="col"><b>DELETE</b></th>
              <!-- <th scope="col"><b>TOTAL</b></th> -->
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in cart.items" :key="idx" :id="item.id">
              <td>{{ item.book_id }}</td>
              <td>{{ item.book_name }}</td>
              <td>{{ item.author }}</td>
              <td>{{ item.section }}</td>
              <td :class="{ 'text-green-500': item.status === 'available', 'text-red-500': item.status === 'reserved' }">
                {{ item.status === 'available' ? 'Available' : 'Reserved' }}
              </td> 
              <td>
                <mdicon name="trash-can" class="text-danger" @click="deleteItem(idx, item.book_id)" />
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
            <tr>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td></td>
              <td>
                <button type="button" class="btn btn-sm btn-danger" @click="clearCart">
                  <mdicon name="cart-remove" :height="18" />Clear Requests
                </button>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
      <div v-else>
        <div class="row justify-content-center align-items-center">
          <h2 class="text-center my-5">You have requested for no books!</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { userequestStore } from "@/stores/cartstore.js";
import axiosClient from '@/js/axios.js'


async function fetchRequests() {
  try {
    console.log('Fetching requests...');
    const response = await axiosClient.get(`/api/request`);
    const items = response.data;
    console.log(response.data);
    localStorage.setItem('request', JSON.stringify(items));
  } catch (error) {
    console.error('Error fetching requests:', error);
    throw error; // Throw the error to be handled by the caller
  }
}

// Call fetchRequests to fetch the items and store the length of items
fetchRequests().catch(error => {
  console.error('Error:', error);
});
let cart = userequestStore();
const deleteItem = async (id, book_id) => {
  try {
    const resp = await axiosClient.delete(`/api/request/${book_id}`);
    console.log(resp);
    console.log("delete item event");
    cart.items.splice(id, 1);
    cart.update();
  } catch (error) {
    console.error("Error deleting item:", error);
    // Handle error as needed
  }
};

const clearCart = async () => {
  try {
    for (const item of cart.items) {
      const resp = await axiosClient.delete(`/api/request/${item.book_id}`);
      console.log(resp);
    }   
    cart.items = [];
    cart.update();
  } catch (error) {
    console.error("Error clearing cart:", error);
    // Handle error as needed
  }
};


</script>

<style scoped></style>
