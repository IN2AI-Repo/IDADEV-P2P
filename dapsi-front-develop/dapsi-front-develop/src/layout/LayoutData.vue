<template>
  <div class="flex h-screen">
    <left-menu class="leftMenu bg-white shadow-sm overflow-x-auto" />
    <div class="flex-1 bg-dapsi-gray-200 overflow-x-auto">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import LeftMenu from '@/components/LeftMenu'
export default {
  name: 'LayoutData',
  components: {
    LeftMenu
  }
}
</script>

<style lang="postcss">
  .leftMenu {
    width: 300px;
  }
</style>