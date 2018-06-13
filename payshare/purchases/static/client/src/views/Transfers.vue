<template>

<div>
  <!-- Upper pagination controls -->
  <v-layout justify-center>
    <v-pagination v-if="numPages > 0"
                  :length="numPages"
                   v-model="pageIndex"
                   :disabled="busy">
    </v-pagination>
  </v-layout>
  <!-- Transfers list of current Page-->
  <v-layout column>
    <purchase v-for="(purchase, purchaseIndex) in purchases"
              :key="purchaseIndex"
              :purchase="purchase">
    </purchase>
  </v-layout>
  <!-- Lower pagination controls -->
  <v-layout justify-center>
    <v-pagination v-if="numPages > 0 && purchases.length > 6"
                  :length="numPages"
                   v-model="pageIndex"
                   :disabled="busy">
    </v-pagination>
  </v-layout>
</div>

</template>

<script>

import Purchase from '@/components/Purchase'

export default {
  name: 'Transfers',
  components: {
    Purchase,
  },
  computed: {
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
