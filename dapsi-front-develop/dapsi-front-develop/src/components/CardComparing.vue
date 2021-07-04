<template>
  <div class="">
    <div class="flex items-center">
      <img class="w-14" :src="_pathImage(data.image)" alt="">
      <h2 class="ml-6 text-2xl text-primary-500">{{ data.name }}</h2>
    </div>
    <div class="mt-2 pl-20">
      <p>{{ data.name }} has data about you if:</p>
      <div class="flex mt-1 mb-3">
        <div class="mt-2 mr-1.5 w-1.5 h-1.5 rounded-full bg-gray-800" />
        You have created an {{ data.name }} account.
      </div>
      <p>{{ data.name }} gathers all this information about you:</p>

      <div class="bg-gray-50 border border-gray-300 py-3 px-4 rounded-md mt-3 grid gap-y-4">
        <div
          v-for="(item, index) in data.information_list"
          :key="index"
          class="">
          <div class="flex">
            <img class="h-4 opacity-70 transform rotate-90 mr-3" src="../assets/icons/arrow-right.png">
            <h3 class="text-primary-500 mb-2 leading-none">{{item.name}}</h3>
          </div>
          <div
            v-for="(child, i) in item.list"
            :key="i"
            class="flex text-sm pl-7">
              <div class="mt-1.5 mr-1.5 w-1.5 h-1.5 rounded-full bg-gray-800" />
              {{child}}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardComparing',
  props: {
    data: {
      default: () => ({})
    }
  },
  methods: {
    _pathImage (img) {
      return require(`@/assets/company/${img}.png`)
    } 
  }
}
</script>