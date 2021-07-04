<template>
  <div id="Step" class="pb-8 relative step">
    <div class="flex h-12 items-center relative z-40">
      <div class="w-12 flex justify-center">
        <div
          :class="[
            {'bg-primary-100': done}, 
            {'w-12 h-12': step === current}
          ]"
          class="border-4 border-primary-100 text-primary-100 bg-white font-title text-2xl rounded-full w-6 h-6 flex justify-center items-center transition-all">
          <span v-if="step === current">{{step}}</span>
          <img v-else-if="step < current" src="../assets/icons/check.png">
        </div>
      </div>
      <h3
        v-if="done || step === current"
        :class="[
          { 'text-opacity-60 text-primary': step < current },
        ]"
        class="pl-4 font-title text-primary-100 text-xl">{{ title }}</h3>
    </div>
    <collapse-transition :duration="300">
      <div class="content" v-show="step === current">
        <slot />
      </div>
    </collapse-transition>
  </div>
</template>

<script>
import { CollapseTransition } from "@ivanv/vue-collapse-transition"
export default {
  name: 'Step',
  props: {
    title: {
      default: ''
    },
    done: {
      default: false
    },
    step: {
      default: 1
    },
    current: {
      default: 1
    },
    change: {
      default: () => ({})
    }
  },
  components: {
    CollapseTransition
  },
  methods: {
    _change () {
      if (this.step < this.current) {
        console.log(`wq`)
        this.$emit('change', this.step)
      }
    }
  }
}
</script>

<style lang="postcss">
  .step::after {
    content: '';
    @apply absolute w-1 bg-primary-100 top-5;
    left: 22px;
    height: 100%;
    z-index: -1px;
  }
  .step:last-child::after {
    display: none;
  }
  .content {
    margin-left: 66px;
  }
</style>