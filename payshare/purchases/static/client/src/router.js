import Vue from 'vue'
import Router from 'vue-router'

import Login from './views/Login.vue'
import Unknown from './views/Unknown.vue'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/unknown',
      name: 'unknown',
      component: Unknown
    },
    {
      path: '/:key',
      name: 'login',
      component: Login
    },
  ]
})
