<template>
  <div
    id="CardAcademy"
    :to="{ name: 'company-detail', params: { id: data.id } }"
    class="
    inline-block
    bg-white
    rounded-md
    border
    border-gray-200
    p-5">
    <h2 class="text-primary-500 text-lg leading-none mb-1">{{data.title}}</h2>
    <p class="text-gray-400 leading-none">{{data.origin}}</p>
    <div class="grid grid-cols-1 lg:grid-cols-2 mt-4 mb-5">
      <img class="object-cover h-28 w-full" :src="_pathImage(data.image)">
      <div class="px-3 pt-2 lg:pt-0 leading-5" v-text="data.description" />
    </div>
    <div class="flex justify-end">
      <button
        @click="_openUrl"
        class="flex items-center rounded-md px-3 py-3 text-primary font-title bg-primary-50 transition hover:bg-primary-100 hover:text-white">
        <span class="mr-10 leading-none">Learn now</span>
        <img class="ml-auto w-5" src="../assets/icons/arrow-right.png">
      </button>
    </div>
  </div>
</template>

<script>
// const { shell } = window.require('electron')
export default {
  name: 'CardAcademy',
  props: {
    data: {
      default: () => ({}),
    },
  },
  components: {
  },
  methods: {
    _pathImage (img) {
      return require(`@/assets/academy/${img}`)
    },
    _openUrl () {
      if (window.shellElectron) {
        window.shellElectron.openExternal(this.data.url)
      } else {
        window.open(this.data.url, '_blank');
      }
    }
  }
}
</script>

<style lang="postcss">
</style>