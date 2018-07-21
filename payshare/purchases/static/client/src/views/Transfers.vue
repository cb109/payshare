<template>

<div>
  <v-layout justify-center>
    <v-flex md8>
      <v-tabs v-model="currentTabIdx"
              grow
              fixed-tabs>
        <v-tab v-for="(tab, tabIndex) in tabs"
               :key="tabIndex">
          {{ $t(tab.title) }}
        </v-tab>
        <!-- Feed -->
        <v-tab-item href="feed">
          <v-container>
            <v-layout justify-center>
              <v-flex xs12 sm6>
                <v-text-field
                  append-icon="search"
                  class="pt-0 mt-0"
                  clearable
                  v-model="searchText"
                  :hint="numOverallMatchingTransfers + ' ' + $t('matchingEntries')"
                  persistent-hint
                  @keyup.esc="searchText = ''"
                  @keyup.enter=""
                ></v-text-field>
              </v-flex>
            </v-layout>
            <!-- Upper pagination controls -->
            <v-layout justify-center>
              <v-pagination v-if="numPages > 1"
                            :length="numPages"
                             v-model="pageIndex"
                             :disabled="busy"
                             class="custom-pagination-controls"
                             :total-visible="maxVisiblePaginationItems">
              </v-pagination>
            </v-layout>
            <!-- Transfers list of current Page-->
            <v-layout justify-center>
              <v-flex xs12>
                <template v-for="(transfer, transferIndex) in transfers">
                  <purchase v-if="transfer.kind === 'purchase'"
                            :key="transfer.kind + pageIndex + transferIndex"
                            :purchase="transfer">
                  </purchase>
                  <liquidation v-if="transfer.kind === 'liquidation'"
                               :key="transfer.kind + pageIndex + transferIndex"
                               :liquidation="transfer">
                  </liquidation>
                </template>
              </v-flex>
            </v-layout>
            <!-- Lower pagination controls -->
            <v-layout justify-center>
              <v-pagination v-if="numPages > 1 && transfers.length > 6"
                             class="custom-pagination-controls"
                            :length="numPages"
                             v-model="pageIndex"
                             :disabled="busy"
                             :total-visible="maxVisiblePaginationItems">
              </v-pagination>
            </v-layout>
            <div style="height: 60px"></div>
          </v-container>
        </v-tab-item>
        <!-- Ranking -->
        <v-tab-item href="ranking">
          <v-container class="px-0">
            <ranking-list></ranking-list>
          </v-container>
        </v-tab-item>
        <!-- Cashing Up -->
        <v-tab-item href="cashingUp">
          <v-container class="px-0">
            <cashing-up></cashing-up>
          </v-container>
        </v-tab-item>
      </v-tabs>
    </v-flex>
  </v-layout>
</div>

</template>

<script>

import CashingUp from '@/components/CashingUp'
import Liquidation from '@/components/Liquidation'
import Purchase from '@/components/Purchase'
import RankingList from '@/components/RankingList'

// From https://davidwalsh.name/javascript-debounce-function
function debounce(func, wait, immediate) {
  let timeout;
  return function() {
    const context = this
    const args = arguments
    const later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func.apply(context, args)
  }
}

export default {
  name: 'Transfers',
  components: {
    CashingUp,
    Liquidation,
    Purchase,
    RankingList,
  },
  data() {
    return {
      currentTabIdx: null,
      tabs: [
        {id: 1, title: 'feed'},
        {id: 2, title: 'ranking'},
        {id: 3, title: 'cashingUp'},
      ],
    }
  },
  computed: {
    searchText: {
      get() {
        return this.$store.state.searchText
      },
      set(text) {
        this.$store.commit('SET_SEARCH_TEXT', text)
      },
    },
    maxVisiblePaginationItems() {
      // See Vuetify source: src/components/VPagination/VPagination.js:items()
      // The default logic does not use available width in an optimal way,
      // resulting often just two buttons being shown. This improves
      // that a bit, which makes it easier to use on small devices.
      const numItems = Math.floor((this.$vuetify.breakpoint.width - 96) / 30);
      return numItems;
    },
    busy() {
      return this.$store.state.busy
    },
    numPages() {
      return this.$store.state.transfersPage.num_pages
    },
    pageIndex: {
      get() {
        return this.$store.state.transfersPageIndex
      },
      set(index) {
        this.$store.dispatch('UPDATE_TRANSFERS_PAGE_INDEX', index)
      },
    },
    transfers() {
      return this.$store.state.transfersPage.results
    },
    numOverallMatchingTransfers() {
      return this.$store.state.transfersPage.count
    },
  },
  watch: {
    searchText: {
      handler: debounce(function(text) {
        this.$store.commit('RESET_TRANSFERS_PAGE_INDEX')
        this.$store.dispatch('LIST_TRANSFERS')
      }, 300),
    },
  },
  mounted() {
    this.$store.dispatch('LIST_TRANSFERS')
  },
}

</script>

<style lang="stylus">

$smaller-margin = 2px

@media(max-width: 599px)
  .custom-pagination-controls .pagination__item
    width: 1.75rem
    height: 2rem
    margin-left: $smaller-margin
    margin-right: $smaller-margin

  .custom-pagination-controls .pagination__navigation
    margin-left: $smaller-margin
    margin-right: $smaller-margin

</style>