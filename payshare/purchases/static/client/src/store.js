import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// TODO: Get this from the process.env
const apiBaseUrl = 'http://localhost:8000'

export default new Vuex.Store({
  state: {
    collective: null,
    transfers: [],
  },
  getters: {
    isLoggedIn(state) {
      return state.collective !== null
    },
  },
  mutations: {
    LOAD_COLLECTIVE_FROM_LOCALSTORAGE(state) {
      const collectiveString = localStorage.getItem('collective')
      if (collectiveString) {
        const collective = JSON.parse(collectiveString)
        if (collective) {
          state.collective = collective
        }
      }
    },
    SET_COLLECTIVE(state, collective) {
      state.collective = collective
      localStorage.setItem('collective', JSON.stringify(collective))
    },
    UNSET_COLLECTIVE(state) {
      state.collective = null
      localStorage.removeItem('collective')
    },
    SET_TRANSFERS(state, transfers) {
      state.transfers = transfers
    },
  },
  actions: {
    RETRIEVE_COLLECTIVE_USING_CREDENTIALS(context, opts) {
      const url = `${apiBaseUrl}/api/v1/${opts.uuid}`
      const config = {
        'headers': {
          'authorization': opts.password,
        },
      }
      return axios.get(url, config).then(response => {
        const collective = response.data
        context.commit('SET_COLLECTIVE', collective)
      })
    },
    LIST_TRANSFERS(context) {
      const uuid = context.state.collective.key
      const token = context.state.collective.token
      const url = `${apiBaseUrl}/api/v1/${uuid}/transfers`
      const config = {
        'headers': {
          'authorization': 'Token ' + token,
        },
      }
      return axios.get(url, config).then(response => {
        const transfers = response.data
        context.commit('SET_TRANSFERS', transfers)
      })
    },
  }
})
