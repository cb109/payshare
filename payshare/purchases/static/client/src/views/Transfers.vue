<template>

<div>
  <v-layout justify-center>
    <v-pagination v-if="numPages > 0"
                  :length="numPages"
                   v-model="pageIndex">
    </v-pagination>
  </v-layout>
  <ul>
    <li v-for="(transfer, transferIndex) in transfers"
        :key="transferIndex">
      {{ transfer.created_at }}
      {{ transfer.name }}
    </li>
  </ul>
</div>

</template>

<script>

export default {
  name: 'Transfers',
  data() {
    return {

    }
  },
  computed: {
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
  },
  mounted() {
    this.$store.dispatch('LIST_TRANSFERS')
  },
}

</script>

