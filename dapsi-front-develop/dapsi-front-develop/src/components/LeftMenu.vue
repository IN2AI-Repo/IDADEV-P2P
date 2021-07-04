<template>
  <div id="leftMenu" class="flex flex-col pb-6">
    <router-link class="inline-block p-6 item" :to="{name: 'dashboard'}"> 
      <img class="w-44" src="../assets/logo.png" alt="personal data store">
    </router-link>
    <ul class="flex-1 px-6 mb-10 list-none m-0 w-auto text-left">
      <li>
        <router-link class="item p-2 py-3 flex transition opacity-70 hover:opacity-100" :to="{name: 'dashboard'}"> 
          <img class="mr-2" src="../assets/icons/dashboard.png"> 
          Dashboard
        </router-link>
      </li>
      <li>
        <router-link class="item p-2 py-3 flex transition opacity-70 hover:opacity-100" :to="{name: 'mydata'}"> 
          <img class="mr-2" src="../assets/icons/mydata.png"> 
          My data
        </router-link>
      </li>
      <li>
        <router-link class="item p-2 py-3 flex transition opacity-70 hover:opacity-100" :to="{ name: 'marketplace' }"> 
          <img class="mr-2" src="../assets/icons/marketplace.png"> 
          Marketplace
        </router-link>
      </li>
      <li>
        <router-link class="item p-2 py-3 flex transition opacity-70 hover:opacity-100" :to="{ name: 'data-academy' }"> 
          <img class="mr-2" src="../assets/icons/academy.png"> 
          Data academy
        </router-link>
      </li>
    </ul>
    <Chat class="pr-6 pl-2" />
  </div>
</template>

<script>
import Chat from '@/components/Chat'
export default {
  name: 'LeftMenu',
  components: {
    Chat
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