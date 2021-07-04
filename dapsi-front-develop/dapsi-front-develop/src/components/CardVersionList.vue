<template>
  <div id="CardVersionList" class="flex-1">
    <div
      v-if="data.shared.length"
      class="divide-y divide-gray-200 bg-white flex-1 border-t border-b border-gray-300">
      <div
        v-for="(child, i) in data.shared"
        :key="`${child.company}${i}`"
        class="
        divide-y
        divide-gray-200
        bg-white
        hover:bg-primary-50
        transition-all
        flex-1">
        <div class="
          flex
          items-center
          justify-between
          py-2
          px-3">
          <div class="flex items-center w-40">
            <img
              class="w-8 h-8"
              :src="_pathImage(child.image)">
            <p class="ml-4">{{child.company}}</p>
          </div>
          <p class="text-sm">{{$moment(child.date).format('DD MMM YYYY')}}</p>
          <router-link class="text-sm underline cursor-not-allowed text-primary-100 hover:text-primary-500 transition-all" to="">
            See details
          </router-link>
        </div>
      </div>
    </div>
    <div v-else class="text-gray-400 flex-1">
      This version of your data was never transferred to anyone.
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardVersionList',
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