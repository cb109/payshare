import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// TODO: Get this from the process.env
const apiBaseUrl = 'http://localhost:8000'

export default new Vuex.Store({
  state: {
    collective: null,
  },
  getters: {
    isLoggedIn(state) {
      return state.collective !== null
    },
  },
  mutations: {
    SET_COLLECTIVE(state, collective) {
      state.collective = collective
    },
  },
  actions: {
    RETRIEVE_COLLECTIVE_USING_CREDENTIALS(context, opts) {
      const url = `${apiBaseUrl}/api/v1/${opts.uuid}`
      const config = {'headers': {
        'authorization': opts.password,
      }}
      return axios.get(url, config).then(response => {
        const collective = response.data
        context.commit('SET_COLLECTIVE', collective)
      })
    },
  }
})
