import Vue from 'vue'
import STORE from '@/store/index'
import VueRouter from 'vue-router'
import LayoutAuth from '@/layout/LayoutAuth.vue'
import LayoutData from '@/layout/LayoutData.vue'
import Dashboard from '../views/Dashboard.vue'
import MyData from '../views/MyData.vue'
import DataAcademy from '../views/DataAcademy.vue'
import Marketplace from '../views/Marketplace.vue'
import CompanyDetail from '../views/CompanyDetail.vue'
import Comparing from '../views/Comparing.vue'
import RecoverData from '../views/RecoverData.vue'
import Transfer from '../views/Transfer.vue'
import MarketplaceDetail from '../views/MarketplaceDetail.vue'
import Login from '../views/Login.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/auth',
    name: 'auth',
    redirect: 'login',
    component: LayoutAuth,
    children: [
      {
        path: '/login',
        name: 'login',
        component: Login
      },
    ]
  },
  {
    path: '/',
    name: 'Home',
    redirect: 'dashboard',
    component: LayoutData,
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: Dashboard
      },
      {
        path: 'mydata',
        name: 'mydata',
        component: MyData
      },
      {
        path: 'company-detail/:id',
        name: 'company-detail',
        component: CompanyDetail
      },
      {
        path: 'comparing/:company01/vs/:company02',
        name: 'comparing',
        component: Comparing
      },
      {
        path: 'recover-data/:id',
        name: 'recover-data',
        component: RecoverData
      },
      {
        path: 'marketplace',
        name: 'marketplace',
        component: Marketplace
      },
      {
        path: 'marketplace-detail/:id',
        name: 'marketplace-detail',
        component: MarketplaceDetail
      },
      {
        path: 'transfer/:id',
        name: 'transfer',
        component: Transfer
      },
      {
        path: 'data-academy',
        name: 'data-academy',
        component: DataAcademy
      },
    ]
  },
]

const router = new VueRouter({
  mode: 'hash',
  routes,
  scrollBehavior (to) {
    if (to.hash) {
      return {
        selector: to.hash,
        behavior: 'smooth',
      }
    }
  }
})

router.beforeEach((to, from, next) => {
  const auth = STORE.state.is_auth
  if (auth) {
    if (to.name === 'login') next({ name: 'dashboard' })
    else next()
  } else {
    if (to.name === 'login') next()
    else next({ name: 'login' })
  }
})

export default router
