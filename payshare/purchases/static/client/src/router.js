import Vue from 'vue'
import Router from 'vue-router'

import store from './store'

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
      component: Unknown,
    },
    {
      path: '/:key/transfers',
      name: 'transfers',
      component: Transfers,
      meta: { 'requiresAuth': true },
    },
    {
      path: '/:key',
      name: 'login',
      component: Login,
    },
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !store.getters.isLoggedIn) {
    const key = to.params.key
    if (key) {
      return next(`/${key}`)  // To login
    }
    return next('/unknown')
  }
  next()
})

export default router
