<template>
  <div id="CardMarketplace" class="border p-4 rounded-md">
    <div class="flex items-center relative z-10 -mb-1 ml-2">
      <img class="w-8 p-1 border border-gray-100 bg-white shadow-lg rounded-md" :src="_pathImage(companyInterested.image)">
      <p class="text-xs m-0 ml-3 uppercase text-primary-500 font-semibold">{{companyInterested.name}}</p>
    </div>
    <div class="flex items-start">
      <img class="w-11" :src="_pathImage(data.image)">
      <div class="flex flex-col justify-center pl-2">
        <p class="
          text-xs
          leading-none
          text-gray-400">
          is interested in data from
        </p>
        <p class="
          text-xl
          ©-0
          font-title
          text-primary-500">
          {{data.name}}
        </p>
      </div>
    </div>
    <div class="mt-2">
      <p>{{companyInterested.compensation}} compensation. Valid until {{companyInterested.valid_until}}</p>
    </div>
    <div class="flex justify-end mt-8">
      <button
        @click="() => {
          this.$router.push({name: 'marketplace-detail', params: { id: data.id }, query: {interested: companyInterested.id}})
        }"
        :disabled="disabled"
        :class="{'cursor-not-allowed': disabled}"
        class="
        text-primary-500 
        bg-primary-50
        hover:bg-primary-100
        hover:text-white
        transition-all
        py-2
        pl-4
        pr-2
        flex
        justify-between
        rounded-md
        font-bold">
        See more
        <img class="ml-2" src="../assets/icons/arrow-right.png">
      </button>
    </div>
  </div>
</template>

<script>
import {mapState} from 'vuex'
export default {
  name: 'CardMarketplace',
  props: {
    data: {
      default: () => ({})
    },
    id_interested: {
      default: 1
    },
    disabled: {
      default: false
    }
  },
  computed: {
    ...mapState(['companies']),
    companyInterested () {
      return this.companies.filter(item => item.id === this.id_interested)[0]
    }
  },
  methods: {
    _pathImage (img) {
      return require(`@/assets/company/${img}.png`)
    } 
  }
}
</script>