<template>
  <div class="row col-10 m-auto">
    <div class="card shadow-sm mt-4 p-0">
      <div class="card-header m-0 p-0">
        <div class="row col-10 d-flex justify-content-between align-items-center m-auto my-2">
          <div class="col-auto">
            <span class="text-center fs-6 fw-normal mt-3">Sections</span>
          </div>
          <div class="col-10 d-inline-flex justify-content-end m-auto me-0">
            <div class="col-auto mx-2">
              <button class="btn btn-sm btn-secondary mx-2" @click="refresh">
                <mdicon name="refresh" class="text-black" :size="18" />
                <span class="ms-1">Refresh</span>
              </button>
              <button class="btn btn-sm btn-success mx-2" @click="handleSectionAdd({}, false)">
                <mdicon name="shape-square-rounded-plus" class="text-white" :size="18" />
                <span class="ms-1">Add</span>
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="main_loading">
          <loading-indicator></loading-indicator>
        </div>
        <div v-else>
          <div v-if="sections.length > 0">
            <div class="row justify-content-center m-auto">
              <div class="p-0 m-0">
                <div class="table-responsive">
                  <table class="table table-centered table-nowrap rounded">
                    <thead class="table-light">
                      <tr>
                        <th scope="col"><b>ID</b></th>
                        <th scope="col"><b>NAME</b></th>
                        <th scope="col"><b>CREATED</b></th>
                        <th scope="col"><b>UPDATED</b></th>
                        <th scope="col"><b>STATUS</b></th>
                        <th scope="col"><b>REQUEST</b></th>
                        <th scope="col"><b>ACTIONS</b></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(section, idx) in sections"
                        :id="idx"
                        :key="idx"
                        class="align-middle"
                      >
                        <td>{{ section.id }}</td>
                        <td v-if="!section.approved && section.request_type == 'edit'">
                          <s
                            ><span class="text-danger fw-bold">{{ section.name }}</span></s
                          >
                          <mdicon name="arrow-right" class="text-black fw-bolder" :size="16" />
                          <span class="text-success fw-bold">{{ section.request_data }}</span>
                        </td>
                        <td v-else>{{ section.name }}</td>
                        <td>{{ formatDate(section.created_timestamp) }}</td>
                        <td>{{ formatDate(section.updated_timestamp) }}</td>
                        <td v-if="section.approved == true">
                          <span>
                            <mdicon name="check-circle" class="text-success" :size="16" />
                          </span>
                          <span> Approved </span>
                        </td>
                        <td v-else>
                          <span>
                            <mdicon name="clock-time-four" class="text-purple p-1" :size="16" />
                          </span>
                          <span> Pending </span>
                        </td>
                        <td>
                          <span>
                            <span v-html="getSectionType(section)"></span>
                          </span>
                        </td>
                        <td>
                          <button
                            class="btn btn-link dropdown-toggle px-0"
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                          >
                            <mdicon name="dots-horizontal" :width="24" :height="24" />
                          </button>
                          <ul class="dropdown-menu">
                            <li>
                              <a
                                class="dropdown-item"
                                href="javascript: void(0)"
                                @click="handleSectionAdd(section, true)"
                              >
                                <!-- <b><mdicon name="shape-square-rounded-plus" class="text-indian-red" :size="16"/></b> -->
                                <svg
                                  width="20px"
                                  height="20px"
                                  viewBox="0 0 24 24"
                                  fill="text-gray"
                                  xmlns="http://www.w3.org/2000/svg"
                                >
                                  <path
                                    fill-rule="evenodd"
                                    clip-rule="evenodd"
                                    d="M21.1213 2.70705C19.9497 1.53548 18.0503 1.53547 16.8787 2.70705L15.1989 4.38685L7.29289 12.2928C7.16473 12.421 7.07382 12.5816 7.02986 12.7574L6.02986 16.7574C5.94466 17.0982 6.04451 17.4587 6.29289 17.707C6.54127 17.9554 6.90176 18.0553 7.24254 17.9701L11.2425 16.9701C11.4184 16.9261 11.5789 16.8352 11.7071 16.707L19.5556 8.85857L21.2929 7.12126C22.4645 5.94969 22.4645 4.05019 21.2929 2.87862L21.1213 2.70705ZM18.2929 4.12126C18.6834 3.73074 19.3166 3.73074 19.7071 4.12126L19.8787 4.29283C20.2692 4.68336 20.2692 5.31653 19.8787 5.70705L18.8622 6.72357L17.3068 5.10738L18.2929 4.12126ZM15.8923 6.52185L17.4477 8.13804L10.4888 15.097L8.37437 15.6256L8.90296 13.5112L15.8923 6.52185ZM4 7.99994C4 7.44766 4.44772 6.99994 5 6.99994H10C10.5523 6.99994 11 6.55223 11 5.99994C11 5.44766 10.5523 4.99994 10 4.99994H5C3.34315 4.99994 2 6.34309 2 7.99994V18.9999C2 20.6568 3.34315 21.9999 5 21.9999H16C17.6569 21.9999 19 20.6568 19 18.9999V13.9999C19 13.4477 18.5523 12.9999 18 12.9999C17.4477 12.9999 17 13.4477 17 13.9999V18.9999C17 19.5522 16.5523 19.9999 16 19.9999H5C4.44772 19.9999 4 19.5522 4 18.9999V7.99994Z"
                                    fill="#000"
                                  />
                                </svg>
                                Edit
                              </a>
                            </li>
                            <div v-if="role == 'admin'">
                              <li v-if="!section.approved">
                                <a
                                  class="dropdown-item"
                                  href="javascript: void(0)"
                                  @click="handleSectionApprove(section, true)"
                                >
                                  <mdicon name="check-circle" class="text-success" :size="20" />
                                  Approve
                                </a>
                              </li>
                              <li v-if="!section.approved">
                                <a
                                  class="dropdown-item"
                                  href="javascript: void(0)"
                                  @click="handleSectionApprove(section, false)"
                                >
                                  <mdicon name="close-circle" class="text-warning" :size="20" />
                                  Reject
                                </a>
                              </li>
                            </div>
                          </ul>
                          <button
                            class="btn btn-link text-decoration-none px-0"
                            aria-expanded="false"
                          >
                            <mdicon
                              name="close-circle"
                              :size="20"
                              class="text-danger p-1"
                              @click="handleSectionDelete(section.id)"
                            />
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
            <h4 class="text-center mt-1">No Sections. Add one!</h4>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal Windows -->

  <!-- Add/Edit Section -->
  <div
    class="modal fade"
    id="modalSection"
    data-bs-backdrop="static"
    data-bs-keyboard="false"
    tabindex="-1"
    aria-labelledby="staticBackdropLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h1 v-if="!edit" class="modal-title fs-5" id="staticBackdropLabel">Add Section</h1>
          <h1 v-else class="modal-title fs-5" id="staticBackdropLabel">Update Section</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <form
            @submit.prevent="handleSectionModalEdit"
            needs-validation
            novalidate
            :class="{ 'was-validated': wasValidated }"
          >
            <div class="form-floating mb-3">
              <input
                type="text"
                class="form-control"
                :class="{ 'form-control': true, 'is-invalid': errors.name }"
                id="floatingInput"
                placeholder="Fruits/Vegetables"
                v-model="data.name"
                required
              />
              <label for="floatingInput">Section</label>
              <div class="invalid-feedback">
                <span>Section name cannot be empty</span>
              </div>
            </div>
            <div class="modal-footer text-center">
              <button v-if="edit" type="submit" class="btn btn-sm btn-success">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else><mdicon name="update" class="text-white" :size="18" /></span>
                Update
              </button>
              <button v-else type="submit" class="btn btn-sm btn-success">
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                <span v-else
                  ><mdicon name="shape-square-rounded-plus" class="text-white" :size="18"
                /></span>
                Add
              </button>
              <button
                type="button"
                class="btn btn-sm btn-danger"
                id="sectionModalClose"
                data-bs-dismiss="modal"
              >
                <mdicon name="window-close" class="text-white" :size="18" />
                Close
              </button>
            </div>
          </form>
          <div class="row d-flex justify-content-center" v-if="errordata.isError">
            <div class="col-11 text-center">
              <div class="alert alert-danger" role="alert">
                {{ errordata.msg }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Section -->
  <div class="modal fade" id="modalSectionDelete" role="dialog" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Delete Section</h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <p>This will delete the section and all the products under this</p>
          <p>This action is irreversible</p>
          <p>Are you sure you want to do this?</p>
        </div>
        <div class="modal-footer">
          <button @click="handleSectionModalDelete" type="button" class="btn btn-danger">
            <span v-if="loading" class="spinner-border spinner-border-sm"></span>
            <span v-else><mdicon name="delete" class="text-white" :size="16" /></span>
            Delete
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <mdicon name="window-close" class="text-white" :size="18" />
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axiosClient from '@/js/axios.js'
import { useAuthStore } from '@/stores/authstore.js'
// import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import LoadingIndicator from '@/components/LoadingIndicator.vue'

const auth = useAuthStore()

// data
const role = ref(auth.user.role)
const sections = ref([])
const errordata = reactive({
  isError: false,
  msg: ''
})
const errors = reactive({
  name: false
})

function formatDate(timestamp) {
  const date = new Date(timestamp)
  const options = {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }
  return date.toLocaleDateString('en-IN', options)
}

let modal
let modalDelete
const main_loading = ref(true)
const loading = ref(false)
const data = reactive({
  id: 0,
  name: ''
})
const section_name = ref('') //keep a copy of the section name during the modal
const edit = ref(false)
const wasValidated = ref(false)

// Main Functions
onMounted(async () => {
  // refreshSections()

  modal = new Modal(document.getElementById('modalSection'), {
    keyboard: false
  })

  modalDelete = new Modal(document.getElementById('modalSectionDelete'), {
    keyboard: false
  })
})

function getSectionType(section) {
  if (section.approved) return '<span class="badge rounded-pill bg-secondary"><b>OK</b></span>'
  else {
    if (section.request_type == 'add') {
      return '<span class="badge rounded-pill bg-success"><b>ADD</b></span>'
    } else if (section.request_type == 'edit') {
      return '<span class="badge rounded-pill text-dark bg-warning"><b>EDIT</b></span>'
    } else if (section.request_type == 'delete') {
      return '<span class="badge rounded-pill bg-danger"><b>DELETE</b></span>'
    } else {
      return ''
    }
  }
}

async function refreshSections() {
  console.log('refreshing sections')
  main_loading.value = true
  try {
    const resp = await axiosClient.get('/api/section')
    console.log(resp)
    sections.value = resp.data
  } catch (err) {
    console.log('Error: ', err)
  } finally {
    main_loading.value = false
  }
}

const refresh = async () => {
  await refreshSections()
}

async function handleSectionApprove(section, approve) {
  loading.value = true

  try {
    if (section.request_type == 'edit') {
      const formData = new FormData()
      formData.append('name', section.name)
      formData.append('approved', approve)
      console.log(formData)
      const resp = await axiosClient.put(`/api/section/${section.id}`, formData)
      console.log(resp)
    } else if (section.request_type == 'add') {
      if (approve) {
        const formData = new FormData()
        formData.append('name', section.name)
        formData.append('approved', approve)
        console.log(formData)
        const resp = await axiosClient.put(`/api/section/${section.id}`, formData)
        console.log(resp)
      } else {
        const resp = await axiosClient.delete(`/api/section/${section.id}`)
        console.log(resp)
      }
    } else {
      if (!approve) {
        const formData = new FormData()
        formData.append('name', section.name)
        formData.append('approved', false)
        console.log(formData)
        const resp = await axiosClient.put(`/api/section/${section.id}`, formData)
        console.log(resp)
      } else {
        const resp = await axiosClient.delete(`/api/section/${section.id}`)
        console.log(resp)
      }
    }
    refreshSections()
  } catch (err) {
    console.log(err)
  } finally {
    loading.value = false
  }
}

function handleSectionAdd(section, isEdit) {
  console.log('Add/Edit Section:', section)

  errordata.isError = false
  errordata.msg = ''
  wasValidated.value = false
  errors.name = false

  section_name.value = section.name
  if (isEdit) {
    data.id = section.id
    data.name = section.name
  } else {
    data.id = 0
    data.name = ''
  }
  edit.value = isEdit

  modal.show()
}

const handleSectionDelete = async (id) => {
  console.log('Delete Section:', id)
  errordata.isError = false
  errordata.msg = ''

  data.id = id
  modalDelete.show()
}

// Modal Functions
async function handleSectionModalEdit() {
  wasValidated.value = false
  errordata.isError = false
  errordata.msg = ''

  if (data.name === '') {
    errordata.isError = true
    errordata.msg = 'Section name cannot be empty'
    errors.name = true
    return
  }

  wasValidated.value = true

  const formData = new FormData()
  if (edit.value) {
    formData.append('name', section_name.value)
    formData.append('request_type', 'edit')
  } else {
    formData.append('name', data.name)
    formData.append('request_type', 'add')
  }
  formData.append('request_data', data.name)

  loading.value = true
  let resp = {}
  try {
    if (edit.value) resp = await axiosClient.put(`/api/section/${data.id}`, formData)
    else resp = await axiosClient.post('/api/section', formData)

    console.log(resp)
    console.log('modal: closing modal')
    document.getElementById('sectionModalClose').click()
    modal.hide()
    refreshSections()
  } catch (err) {
    console.log(err)
    errordata.isError = true
    errordata.msg = err.response.data
  } finally {
    // data.name = ''
    // errordata.isError = false
    // errordata.msg = ''
    wasValidated.value = false
    loading.value = false
  }
}

async function handleSectionModalDelete() {
  console.log('modal:Delete Section')

  loading.value = true
  try {
    const resp = await axiosClient.delete(`/api/section/${data.id}`)
    console.log(resp)
    console.log('modal: closing modal')
    document.getElementById('sectionModalClose').click()
    modal.hide()
    refreshSections()
  } catch (err) {
    console.log(err)
    errordata.isError = true
    errordata.msg = err.response.data
  } finally {
    data.name = ''
    // errordata.isError = false
    errordata.msg = ''
    loading.value = false
  }

  modalDelete.hide()
  refreshSections()
}

await refreshSections()
</script>

<style scoped>
th {
  vertical-align: middle;
  border-bottom: 3px solid #485460;
  font-size: 12px, bold;
}
.dropdown-toggle::after {
  content: none;
}
</style>
