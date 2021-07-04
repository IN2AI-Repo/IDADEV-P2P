<template>
  <div id="CardVersionMini" class="flex hover:bg-green-100 hover:border-green-300 transition-all cursor-pointer">
    <div class="">
      <h6 class="font-lato">{{data.date}}</h6>
      <p class="text-xs capitalize">{{SizeFile(data.size)}}</p>
    </div>
  </div>
</template>

<script>
import Minxin from '@/minxis/global'
export default {
  name: 'CardVersionMini',
  mixins: [Minxin],
  props: {
    data: {
      default: () => ({})
    }
  },
}
</script>