import Vue from 'vue'
import VueI18n from 'vue-i18n'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

import App from './App.vue'
import messages from './translations';
import router from './router'
import store from './store'
import './registerServiceWorker'

Vue.use(VueI18n)
Vue.use(Vuetify, {
  theme: {
    primary: '#0000d6',
  },
})
Vue.config.productionTip = false

const defaultLocale = (navigator.language ||
                       navigator.userLanguage).slice(0, 2);
const i18n = new VueI18n({
  locale: defaultLocale,
  messages,
})

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
