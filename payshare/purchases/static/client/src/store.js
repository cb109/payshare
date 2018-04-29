import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    collective: null,
    token: null,
  },
  mutations: {
    SET_TOKEN(state, token) {

    },
  },
  actions: {
    RETRIEVE_COLLECTIVE_USING_CREDENTIALS(uuid, password) {

    },
  }
})
