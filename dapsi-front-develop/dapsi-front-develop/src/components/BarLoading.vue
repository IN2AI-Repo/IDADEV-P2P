<template>
  <div class="">
    <div class="relative w-full pt-3">
      <div class="h-3 bg-gray-200 rounded-md"></div>
      <div class="absolute flex flex-col left-0 top-0 w-full">
        <div class="flex flex-col transition-all" :style="{ width: `${current.porcentage}%` }">
          <div
            class="bg-primary rounded-2xl h-8 flex justify-end items-center pr-2">
            <img v-if="current.description !== 'Complete'" class="animate-spin w-5" src="../assets/icons/loading.png">
            <img v-else class=" w-5" src="../assets/icons/check.png">
          </div>
          <div class="text-xs mt-1 text-primary self-end">
            {{current.name}}
          </div>
        </div>
      </div>
    </div>
    <ul class="mt-12">
      <li class="flex items-center mb-5" v-for="(item, index) in progress" :key="index">
        <div v-if="current.index > index+1" class="">
          <div class="mr-2 border-2 border-primary bg-primary w-4 h-4 rounded-full">
            <img class="w-4 mr-2" src="../assets/icons/check.png">
          </div>
        </div>
        <div v-else class="flex">
          <img v-if="item.name === current.name" class="animate-spin w-4 mr-2" src="../assets/icons/loading-primary.png">
          <span v-else class="mr-2 border-2 border-primary w-4 h-4 rounded-full"></span>
        </div>
        {{item.description}}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'BarLoading',
  props: {
    progress: {
      default: () => []
    },
  },
  data () {
    return({
      current: {
        name: 'Starting',
        description: 'Starting',
        porcentage: 10,
        timer: 3000,
        index: 0,
      }
    })
  },
  mounted () {
    this._progress()
  },
  methods: {
    async _progress () {
      const progress = this.progress
      const divition = 100 / progress.length
      let porcentage = 0
      for (let i = 0; i < progress.length; i++) {
        const item = progress[i];
        porcentage = porcentage + divition
        this.current = {
          ...item,
          porcentage,
          index: i + 1,
        }
        await new Promise(resolve => setTimeout(resolve, item.timer));
      }
      this.current = {
        name: 'All done!',
        description: 'Complete',
        porcentage: 100,
        timer: 3000,
        index: this.current.index + 1
      }
      await new Promise(resolve => setTimeout(resolve, 2000));
      this.$emit('complete')
    }
  }
}
</script>

<style lang="postcss" scoped>

</style>