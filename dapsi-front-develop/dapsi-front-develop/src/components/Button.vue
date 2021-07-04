<template>
  <button
    :disabled="disabled"
    type="type"
    @click="$emit('click')"
    :class="[
      {'cursor-not-allowed': disabled},
      disabledStyl,
      dark ? 'bg-primary' : 'bg-primary-50',
    ]"
    class="
      items-center
      rounded-lg
      px-6
      py-3
      font-title
      font-light
      transition-all
      group
      hover:bg-primary-100">
    <p
      v-if="title"
      :class="[dark ? 'text-white' : 'text-primary group-hover:text-white',]"
      class="leading-none whitespace-nowrap transition-all">
        {{ title }}
    </p>
    <slot v-else />
  </button>
</template>

<script>
export default {
  name: 'Button',
  props: {
    title: {
      default: ''
    },
    disabled: {
      default: false
    },
    type: {
      default: ''
    },
    dark: {
      default: false
    },
    click: {
      default: () => ({})
    }
  },
  computed: {
    checkStep () {
      return this.stepsActive.includes(this.step)
    },
    disabledStyl () {
      if (this.disabled) {
        return this.dark ? 'bg-opacity-40 text-primary cursor-not-allowed' : 'bg-opacity-40 text-primary-500'
      }
      return ''
    }
  },
  methods: {
    _change () {
      if (this.checkStep) {
        this.$emit('change', this.step)
      }
    }
  }
}
</script>

<style lang="postcss" scoped>
  .circle {
    @apply border-4 border-primary-100 text-primary-100 font-title text-xl rounded-full w-5 h-5 flex justify-center items-center;
  }
  .check {
    @apply bg-primary-100
  }
  .active {
    @apply w-11 h-11
  }
</style>