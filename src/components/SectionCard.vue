<template>
  <div class="card border-secondary m-2 p-0 pb-2" style="width: 20rem;">
  <div class="card-body p-0">
    <img :src='img_src' class="card-img-top object-fit-fit" alt="Section Image">
    <h5 class="card-title text-center">{{ props.section.name }}</h5>
    <div class="d-flex justify-content-around">
        <button class="btn btn-sm btn-success">
            <mdicon name="cog" class="text-white" :size='20' />
            Manage
        </button>
        <button class="btn btn-sm btn-info">
            <mdicon name="pencil-box-outline" class="text-danger" :size='20' />
            Edit
        </button>
        <button class="btn btn-sm btn-danger" data-bs-toggle='modal' data-bs-target="#modalSectionDelete">
            <mdicon name="delete" class="text-white" :size='20' />
            Delete
        </button>
    </div>
  </div>
  <!-- <pre>{{ props }}</pre> -->
    <!-- <pre>{{ props.section.id }}</pre> -->
<!-- <SectionDeleteModal :id="id" :name="props.section.name" /> -->
</div> 

<!-- Section delete modal -->
  <div class="modal fade" id="modalSectionDelete" tabindex="-1" aria-labelledby="modalSectionDeleteLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title fs-5" id="modalSectionDeleteLabel">Delete Section</h2>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <p>
            <b>Deleting section will delete all the products associated with this section.</b>
            Do you want to delete section <b>`${props.section.name}`</b>?
          </p>
            <pre>{{ props }}</pre>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-danger" @click="handleDelete($props.section.id)">Delete {{ props.section.id }}</button>
          <button type="button" class="btn btn-secondary" id='modalSectionDeleteClose' data-bs-dismiss="modal">Cancel</button>
        </div>
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
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
// import SectionDeleteModal from '@/components/SectionDeleteModal.vue';
// import axiosClient from '@/js/axios.js';

const props = defineProps({
  section: {
    id: {
        type: Number,
        required: true,
    },
    name: {
        type: String,
        required: true,
    },
    image: {
        type: String,
        required: true,
    },
    created_timestamp: {
        type: String,
        required: true,
    },
  },
})

// onMounted(() =>{
//     console.log(props.section.id)
// })

const errordata = reactive({
    isError : false,
    msg : ''
})

const img_src=`http://127.0.0.1:5000/images/section/${props.section.image}`

const id=ref(props.section.id)

const handleDelete =(id) => {
    // console.log('from function:', get_section_id())
    console.log('param:', id)
    console.log('Delete Section: ', props.section.name)
    console.log(props.section.id)

    // try {
    //     console.log('modal: section id:', props.section.id, id)
    //     const res = await axiosClient.delete(`/api/section/${props.section.id}`)
    //     console.log(res)
    //     // window.location.reload()
    //     document.getElementById('modalSectionDeleteModal').click()
    //     errordata.isError = false,
    //     errordata.msg = ''
    // } catch (error) {
    //     console.log('Error: ', error)
    //     errordata.isError = true,
    //     errordata.msg = error.message
    // }
}

</script>

<style scoped>
.card-img-top {
    width: 100%;
    height: 150px;
};
</style>