<template>
  <div id="header" class="flex justify-between items-center">
    <h2 class="text-primary-700 text-2xl lg:text-4xl font-bold font-title">{{title}}</h2>
    <div @click="_logout" class="flex items-center">
      <div class="text-right mr-3">
        <p class="font-semibold leading-3">Sierra Ferguson</p>
        <p class="m-0">s.ferguson</p>
      </div>
      <img class="w-12 h-12" src="../assets/user/photo.png" alt="">
    </div>
  </div>
</template>

<script>
import {mapMutations} from 'vuex'
export default {
  name: 'Header',
  props: {
    title: {
      default: 'Title',
    }
  },
  methods: {
    ...mapMutations(['IS_AUTH']),
    _logout () {
      this.IS_AUTH(false)
      this.$router.push({ name: 'login' })
    }
  }
}
</script>