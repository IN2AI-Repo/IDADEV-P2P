<template>
  <router-link
    id="CardCompanyMini"
    :to="{ name: 'company-detail', params: { id: data.id } }"
    class="
    bg-primary-50
    shadow-md
    rounded-md
    border
    border-transparent
    transition
    hover:shadow-lg
    hover:border-primary
    p-4">
    <div class="flex items-center">
      <img class="w-14 h-14" :src="_pathImage(image)">
      <div class="ml-4">
        <h2 class="text-lg leading-none lg:leading-none text-primary-700 font-title capitalize mb-1">{{title}}</h2>
        <p class="text-xs text-gray-500">{{description}}</p>
      </div>
    </div>
  </router-link>
</template>

<script>
export default {
  name: 'CardCompanyMini',
  props: {
    data: {
      default: () => ({}),
    },
    title: {
      default: 'Title',
    },
    description: {
      default: '24 nov 2020'
    },
    image: {
      default: 'amazon'
    }
  },
  methods: {
    _pathImage (img) {
      return require(`@/assets/company/${img}.png`)
    } 
  }
}
</script>

<style lang="scss">
  .item {
    &.router-link-active {
      opacity: 1;
    }
  }
</style>