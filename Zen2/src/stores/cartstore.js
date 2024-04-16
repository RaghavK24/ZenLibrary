import { ref, onMounted } from 'vue'
import { defineStore } from 'pinia'



export const userequestStore = defineStore('requestStore', () => {
  const items = ref([])

  onMounted(() => {
    items.value = JSON.parse(localStorage.getItem('request') || '[]')
  })

  function clear() {
    items.value = []
    localStorage.setItem('request', JSON.stringify(items.value))
  }

  function update() {
    // console.log('updating items...')
    localStorage.setItem('request', JSON.stringify(items.value))
    // console.log('total:', total.value)
  }


  return { items, update, clear }
})


