import Vue from 'vue'
import Router from 'vue-router'

import { isUUID } from './mixins/uuid'
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
  const key = to.params.key

  // Handle invalid UUID in URL.
  if (to.name != 'unknown' && key && !isUUID(key)) {
    return next('/unknown')
  }

  if (!store.getters.isLoggedIn) {
    store.commit('LOAD_COLLECTIVE_FROM_LOCALSTORAGE')
  }

  // Handle URL key points to different Collective then cached one.
  if (store.getters.isLoggedIn && key) {
    const urlKeyDiffersFromRememberedKey = store.state.collective.key != key
    if (urlKeyDiffersFromRememberedKey) {
      store.commit('UNSET_COLLECTIVE')
      return next(`/${key}`)
    }
  }

  // Handle not being logged in we we have to be.
  if (to.meta.requiresAuth && !store.getters.isLoggedIn) {
    return next('/unknown')
  }

  // Handle invalid route path e.g.: /<uuid>/bogus
  // TBD

  next()
})

export default router
