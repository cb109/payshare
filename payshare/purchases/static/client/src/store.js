import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// TODO: Get this from the process.env
const apiBaseUrl = 'http://localhost:8000'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const getInitialState = () => {
  return {
    busy: false,
    collective: null,
    selectedMember: null,
    transfersPageIndex: 1,
    transfersPage: {
      num_pages: 0,
      count: 0,
      previous: null,
      next: null,
      results: [],
    },
  }
}

const store = new Vuex.Store({
  state: getInitialState(),
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
    SET_FINANCIAL_STATS(state, stats) {
      state.collective.stats = stats
      localStorage.setItem('collective', JSON.stringify(state.collective))
    },
    LOAD_SELECTED_MEMBER_FROM_LOCALSTORAGE(state) {
      if (!state.collective) {
        return
      }
      const selectedMemberString = localStorage.getItem('selectedMember')
      if (selectedMemberString) {
        const selectedMember = JSON.parse(selectedMemberString)
        if (selectedMember) {
          const collectiveMemberIds = state.collective.members.map(m => m.id)
          if (!collectiveMemberIds.includes(selectedMember.id)) {
            // Stored member is possibly from another collective,
            // make sure to reset it.
            state.selectedMember = null
            return;
          }
          state.selectedMember = selectedMember
        }
      }
    },
    SET_SELECTED_MEMBER(state, member) {
      state.selectedMember = member
      localStorage.setItem('selectedMember', JSON.stringify(member))
    },
    SET_TRANSFERS_PAGE(state, transfersPage) {
      state.transfersPage = transfersPage
    },
    SET_TRANSFERS_PAGE_INDEX(state, index) {
      state.transfersPageIndex = index
    },
    SET_BUSY(state, busy) {
      state.busy = busy
    },
    RESET_ALL(state) {
      this.commit('UNSET_COLLECTIVE')

      const initial = getInitialState()
      Object.keys(initial).forEach(key => {
        state[key] = initial[key]
      })
    },
  },
  actions: {
    UPDATE_COLLECTIVE_FINANCIAL_STATS(context) {
      const uuid = context.state.collective.key
      const token = context.state.collective.token
      const url = `${apiBaseUrl}/api/v1/${uuid}/stats`
      const config = {
        headers: {
          authorization: 'Token ' + token,
        },
      }
      return axios.get(url, config).then(response => {
        context.commit('SET_FINANCIAL_STATS', response.data)
      })
    },
    CREATE_PURCHASE(context, opts) {
      const uuid = context.state.collective.key
      const token = context.state.collective.token
      const url = `${apiBaseUrl}/api/v1/${uuid}/purchase`
      const config = {
        headers: {
          authorization: 'Token ' + token,
        },
      }
      const payload = {
        buyer: opts.buyerId,
        price: opts.price,
        name: opts.name,
      }
      return axios.post(url, payload, config).then(response => {
        context.dispatch('LIST_TRANSFERS')
        context.dispatch('UPDATE_COLLECTIVE_FINANCIAL_STATS')
      })
    },
    CREATE_LIQUIDATION(context, opts) {
      const uuid = context.state.collective.key
      const token = context.state.collective.token
      const url = `${apiBaseUrl}/api/v1/${uuid}/liquidation`
      const config = {
        headers: {
          authorization: 'Token ' + token,
        },
      }
      const payload = {
        creditor: opts.creditorId,
        debtor: opts.debtorId,
        amount: opts.amount,
        name: opts.name,
      }
      return axios.post(url, payload, config).then(response => {
        context.dispatch('LIST_TRANSFERS')
        context.dispatch('UPDATE_COLLECTIVE_FINANCIAL_STATS')
      })
    },
    DELETE_TRANSFER(context, opts) {
      if (!opts.kind && opts.id) {
        throw('Need kind and id')
      }
      const uuid = context.state.collective.key
      const token = context.state.collective.token
      const url = `${apiBaseUrl}/api/v1/${uuid}/${opts.kind}/${opts.id}`
      const config = {
        headers: {
          authorization: 'Token ' + token,
        },
      }
      return axios.delete(url, config).then(response => {
        context.dispatch('LIST_TRANSFERS')
        context.dispatch('UPDATE_COLLECTIVE_FINANCIAL_STATS')
      })
    },
    RETRIEVE_COLLECTIVE_USING_CREDENTIALS(context, opts) {
      const url = `${apiBaseUrl}/api/v1/${opts.uuid}`
      const config = {
        headers: {
          authorization: opts.password,
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
        headers: {
          authorization: 'Token ' + token,
        },
        params: {
          page: context.state.transfersPageIndex,
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

axios.interceptors.request.use(function (config) {
    // Do something before request is sent
    store.commit('SET_BUSY', true)
    return config;
  }, function (error) {
    // Do something with request error
    store.commit('SET_BUSY', false)
    return Promise.reject(error);
  });

// Add a response interceptor
axios.interceptors.response.use(function (response) {
    // Do something with response data
    store.commit('SET_BUSY', false)
    return response;
  }, function (error) {
    // Do something with response error
    store.commit('SET_BUSY', false)
    return Promise.reject(error);
  });

export default store