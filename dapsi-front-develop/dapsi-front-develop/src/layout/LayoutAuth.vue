<template>
  <div class="flex min-h-screen bg-dapsi-gray-200 items-center justify-center py-28 px-10 lg:px-0">
    <div class="grid
      md:grid-cols-2
      bg-white
      shadow-md
      rounded-xl
      w-full
      lg:max-w-3xl
      divide-x">
      <div class="flex order-2 md:order-1 pr-8 pl-4">
        <Chat listStyle="" :input="false" class="w-full md:pt-0 pb-10" />
      </div>
      <div class="px-12 order-1 md:order-2">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script>
import Chat from '@/components/Chat'
export default {
  name: 'LayoutAuth',
  components: {
    Chat
  }
}
</script>