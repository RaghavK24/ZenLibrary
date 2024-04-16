<template>
  <div>
    <div class="card shadow-sm h-100" style="width: 16rem">
      <img
        class="card-img-top object-fit-contain"
        :src="`data:image/png;base64,${data.image}`"
        alt="product image"
        height="150"
        @click="() => $router.push(`/product/${data.section_id}/${data.id}`)"
      />
      <div class="card-body">
        <div class="row justify-content-between">
          <div class="col">
            <b class="fs-6">{{ data.name }}</b>
          </div>
          <div class="col-auto">
            <span class="text-dark text-right fw-normal fs-6"
              ><b>₹</b><b>{{ data.price }}</b
              ></span
            >
          </div>
        </div>
        <div class="row justify-items-between">
          <div class="p-1">
            <br />
          </div>
          <div class="col d-inline-flex align-items-center">
            <label class="text-center" >{{ data.author }}</label>
          </div>
          <div v-if="isnotAdded || !authenticated" class="col-auto">
            <form @submit.prevent="addToCart(data)">
              <button class="btn btn-success btn-sm">
                <mdicon name="book-plus" :size="20" />Request
              </button>
            </form>
          </div>
          <div v-else class="col-auto">
            <span class="text-success">Requested</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, toRef, onMounted, onUnmounted } from 'vue'
import axiosClient from '@/js/axios.js'
import { useAuthStore } from '@/stores/authstore.js'
import { storeToRefs } from 'pinia'
import { userequestStore } from '@/stores/cartstore.js'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const data = toRef(props, 'data') || {}
const auth = useAuthStore()
let isnotAdded = ref(true)
const {authenticated } = storeToRefs(auth)

const request = userequestStore()





onMounted(() => {
  Added()
  
  // Add event listener for window resize
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // Remove event listener when component is unmounted
  window.removeEventListener('resize', handleResize)
})

// Function to handle window resize event
function handleResize() {
  // Call Added function to update the isnotAdded value based on the current viewport size
  Added()
}

function Added() {
  if (request.items.length === 0) {
    isnotAdded.value = true;
  } else {
    for (const item of request.items) {
      if (item.book_id === data.value.id) {
        isnotAdded.value = false;
        break;
      }
      isnotAdded.value = true;
    }
  }
}

async function addToCart(product) {
  const formData = new FormData()
  formData.append('user_id', auth.user.id)
  formData.append('book_id', product.id)
  formData.append('book_status', product.status)

  let item = {}
  item.user_id = auth.user.id
  item.book_id = product.id
  item.book_status = product.status
  item.book_name = product.name
  item.section = product.section_name
  item.author = product.author

  try {
    const resp = await axiosClient.post(`/api/request`, formData);
    console.log("API Response")
    console.log(resp)
    request.items.push(item)
    console.log('add to cart')
    request.update()
    request.update()
  } catch (err) {
    console.log("API Error")
    console.log(err)
  }
  finally{
    Added()
  }
}



</script>

<style scoped></style>
