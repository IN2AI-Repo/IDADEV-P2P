<template>
  <div id="CardCompany" class="bg-white shadow-md rounded-md p-4">
    <div class="flex items-center -ml-6 mb-4">
      <img class="w-14 h-14" :src="_pathImage(image)">
      <h2 class="ml-4 text-xl lg:text-2xl text-primary-700 font-title capitalize">{{title}}</h2>
    </div>
    <p class="text-sm sm:text-base">Last version recovered in {{$moment(date).format('DD MMM YYYY')}}.</p>
    <div
      v-if="!data.is_pending"
      class="flex mt-6 flex-wrap gap-y-3">
      <router-link class="bg-primary-50 mr-4 py-2 px-3 flex items-center rounded-md hover:bg-primary-100 transition" :to="{ name: 'recover-data', params: { id: data.id } }">
        <img src="../assets/icons/update.png">
      </router-link>
      <router-link
        class="relative bg-primary-50 mr-4 py-2 px-3 flex items-center rounded-md hover:bg-primary-100 transition"
        :to="{
          name: 'company-detail',
          params: { id: data.id },
          query: {location: 'whoInterested'}
        }">
        <img src="../assets/icons/marketplace.png">
        <div
          v-if="data.interested.length"
          class="w-5 h-5 absolute bg-red-500 rounded-full -top-2 -right-2 flex justify-center items-center text-white text-xs">
          {{data.interested.length}}
        </div>
      </router-link>
      <router-link
        class="flex flex-1 items-center rounded-md px-3 py-3 text-primary font-title bg-primary-50 transition hover:bg-primary-100 hover:text-white"
        :to="`company-detail/${data.id}`">
        <span class="mr-1 leading-none">See more</span>
        <img class="ml-auto w-5" src="../assets/icons/arrow-right.png">
      </router-link>
    </div>
    <router-link
      v-else
      class="mt-6 flex justify-center flex-1 rounded-md px-3 py-3 text-white text-center font-title bg-primary transition hover:bg-primary-100 hover:text-white"
      :to="{ name: 'recover-data', params: { id: data.id }, query: {continue: true} }">
      <span class="mr-1 leading-none">Continue</span>
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'CardCompany',
  props: {
    data: {
      default: () => ({}),
    },
    title: {
      default: 'Title',
    },
    date: {
      default: new Date()
    },
    image: {
      default: 'amazon'
    },
    pending: {
      default: false
    }
  },
  methods: {
    _pathImage (img) {
      return require(`@/assets/company/${img}.png`)
    } 
  }
}
</script>