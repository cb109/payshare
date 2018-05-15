import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// TODO: Get this from the process.env
const apiBaseUrl = 'http://localhost:8000'

export default new Vuex.Store({
  state: {
    collective: null,
    transfersPageIndex: 1,
    transfersPage: {
      num_pages: 0,
      count: 0,
      previous: null,
      next: null,
      results: [],
    },
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
    SET_TRANSFERS_PAGE(state, transfersPage) {
      state.transfersPage = transfersPage
    },
    SET_TRANSFERS_PAGE_INDEX(state, index) {
      state.transfersPageIndex = index
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
        'params': {
          'page': context.state.transfersPageIndex,
        }
      }
      return axios.get(url, config).then(response => {
        const transfersPage = response.data
        context.commit('SET_TRANSFERS_PAGE', transfersPage)
      })
    },
    UPDATE_TRANSFERS_PAGE_INDEX(context, index) {
      context.commit('SET_TRANSFERS_PAGE_INDEX', index)
      context.dispatch('LIST_TRANSFERS')
    },
  }
})
