<template>
  <div class="container-fluid">
    <h2 class="text-center mt-3">Dashboard</h2>
    <div class="row justify-content-end">
      <div class="col-auto me-5">
        <button class="btn btn-warning" @click="fetchData">
          <mdicon name="refresh" size="20" />
          Refresh
        </button>
      </div>
    </div>
    <div v-if="loading" class="row justify-content-center mt-5">
      <loading-indicator />
    </div>
    <div v-else class="row g-2">
      <div class="row col-12 justify-content-left m-auto g-2">
        <div class="col-2 d-flex g-3">
          <InfoPill :data="managers" />
        </div>
        <div class="col-2 d-flex g-3">
          <InfoPill :data="users" />
        </div>
        <div class="col-2 d-flex g-3">
          <InfoPill :data="sections" />
        </div>
        <div class="col-2 d-flex g-3">
          <InfoPill :data="books" />
        </div>
        <div class="col-2 d-flex g-3">
          <InfoPill :data="orders_total" />
        </div>
        <div class="col-2 d-flex g-3">
          <InfoPill :data="revenue_total" />
        </div>
      </div>
      <div class="row col-12 mt-3">
        <div class="col-4">
          <BarChart
            :title="ordersBarChartTitle"
            :labels="ordersBarChartLabels"
            :data="ordersBarChartData"
          />
        </div>
        <div class="col-4">
          <PieChart
            :title="sectionPieChartTitle"
            :labels="sectionPieChartLabels"
            :data="sectionPieChartData"
          />
        </div>
        <div class="col-4">
          <BarChart
            :title="revenueBarChartTitle"
            :labels="revenueBarChartLabels"
            :data="revenueBarChartData"
          />
        </div>
      </div>
    </div>
    <!-- <pre> data: {{ data }}</pre> -->
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axiosClient from '@/js/axios.js'
import InfoPill from '@/components/InfoPill.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import PieChart from '@/components/charts/PieChart.vue'
import BarChart from '@/components/charts/BarChart.vue'

const data = ref({})
const loading = ref(false)
const errorinfo = reactive({
  error: false,
  msg: ''
})

const ordersBarChartTitle = ref('')
const ordersBarChartLabels = ref([])
const ordersBarChartData = ref([])

const sectionPieChartTitle = ref('')
const sectionPieChartLabels = ref([])
const sectionPieChartData = ref([])

const revenueBarChartTitle = ref('')
const revenueBarChartLabels = ref([])
const revenueBarChartData = ref([])

const managers = {
  title: 'Managers',
  icon: 'account-multiple',
  color: 'text-primary',
  count: 0
}

const users = {
  title: 'Users',
  icon: 'account-multiple',
  color: 'text-primary',
  count: 0
}

const sections = reactive({
  title: 'Sections',
  icon: 'format-list-bulleted-type',
  color: 'text-secondary',
  count: 0
})

const books = reactive({
  title: 'Books',
  icon: 'format-list-bulleted-type',
  color: 'text-secondary',
  count: 0
})

const orders_total = reactive({
  title: 'Orders',
  icon: 'format-list-bulleted-type',
  color: 'text-secondary',
  count: 0
})

const revenue_total = reactive({
  title: 'Revenue',
  icon: 'format-list-bulleted-type',
  color: 'text-secondary',
  count: 0
})

const fetchData = async () => {
  loading.value = true
  try {
    const resp = await axiosClient.get('/admin')
    data.value = resp.data
    console.log(data.value)

    managers.count = data.value.managers
    users.count = data.value.users
    sections.count = data.value.section
    books.count = data.value.books
    orders_total.count = data.value.orders_total
    revenue_total.count = '₹' + (data.value.revenue_total ? data.value.revenue_total : '0') + '/-'

    // pie chart data for categories
    sectionPieChartTitle.value = 'Sections'
    sectionPieChartLabels.value = data.value.sections.map(function (el) {
      return el.name
    })
    sectionPieChartData.value = data.value.sections.map(function (el) {
      return el.count
    })

    // bar chart data for Orders
    ordersBarChartTitle.value = 'Orders'
    ordersBarChartLabels.value = data.value.orders.map(function (el) {
      return el.date
    })
    ordersBarChartData.value = data.value.orders.map(function (el) {
      return el.count
    })

    // bar chart data for revenue
    revenueBarChartTitle.value = 'Revenue'
    revenueBarChartLabels.value = data.value.revenue.map(function (el) {
      return el.date
    })
    revenueBarChartData.value = data.value.revenue.map(function (el) {
      return el.total
    })
  } catch (err) {
    console.log(err)
    if (err.response) {
      errorinfo.error = true
      errorinfo.msg = err.response.data
    } else {
      errorinfo.error = true
      errorinfo.msg = err.message
    }
  } finally {
    errorinfo.error = false
    errorinfo.msg = ''
    loading.value = false
  }
}

await fetchData()
</script>

<style scoped lang="scss"></style>
