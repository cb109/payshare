import Vue from 'vue'
import Router from 'vue-router'

import Login from './views/Login.vue'
import Transfers from './views/Transfers.vue'
import Unknown from './views/Unknown.vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/unknown',
      name: 'unknown',
      component: Unknown
    },
    {
      path: '/:key/transfers',
      name: 'transfers',
      component: Transfers,
    },
    {
      path: '/:key',
      name: 'login',
      component: Login
    },
  ]
})

export default router
