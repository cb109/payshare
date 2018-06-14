<template>

<div>
  <!-- Upper pagination controls -->
  <v-layout justify-center>
    <v-pagination v-if="numPages > 0"
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
                :key="transferIndex"
                :purchase="transfer">
      </purchase>
      <liquidation v-if="transfer.kind === 'liquidation'"
                   :key="transferIndex"
                   :liquidation="transfer">
      </liquidation>
    </template>
    </v-flex>
  </v-layout>
  <!-- Lower pagination controls -->
  <v-layout justify-center>
    <v-pagination v-if="numPages > 0 && purchases.length > 6"
                   class="custom-pagination-controls"
                  :length="numPages"
                   v-model="pageIndex"
                   :disabled="busy">
    </v-pagination>
  </v-layout>
</div>

</template>

<script>

import Liquidation from '@/components/Liquidation'
import Purchase from '@/components/Purchase'

export default {
  name: 'Transfers',
  components: {
    Liquidation,
    Purchase,
  },
  computed: {
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
    purchases() {
      return this.transfers.filter(transfer => transfer.kind === 'purchase')
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