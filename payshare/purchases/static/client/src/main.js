import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

import App from './App.vue'
import i18n from './i18n';
import router from './router'
import store from './store'
import './registerServiceWorker'

Vue.use(Vuetify, {
  theme: {
    primary: '#0000d6',
  },
})
Vue.config.productionTip = false

/* Setup a global event bus. */
Vue.prototype.$bus = new Vue({})

const app = new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')

export default app
