<template>

<div v-if="collective && selectedMember">
  <v-list three-line
          v-if="sanitizedPaybacks.length">
    <v-list-tile>
      <v-list-tile-content>
        <v-list-tile-title
          class="text-xs-center
                 grey--text
                 text--darken-2
                 list__tile__title--wrap"
        >
          {{ $t('explainCashingUp') }}:
        </v-list-tile-title>
      </v-list-tile-content>
    </v-list-tile>
    <v-divider></v-divider>
  </v-list>
  <v-card v-if="!sanitizedPaybacks.length"
          flat>
    <v-card-title>
      <v-layout justify-center
                align-center>
        <v-icon color="success"
                x-large
                class="mr-2">
          check
        </v-icon>
        <h3 class="headline grey--text text--darken-2">
          {{ $t('nothingToDo') }}
        </h3>
      </v-layout>
    </v-card-title>
  </v-card>
  <v-list v-if="sanitizedPaybacks.length">
    <template v-for="(payback, idx) in selectedMemberPaybacks">
      <payback-list-tile :key="payback.debtor + '_' + payback.creditor"
                         :payback="payback"
                         highlight
                         :divider="idx < selectedMemberPaybacks.length - 1">
      </payback-list-tile>
    </template>
  </v-list>
  <v-divider v-if="otherMemberPaybacks.length"></v-divider>
  <v-list v-if="sanitizedPaybacks.length">
    <template v-for="(payback, idx) in otherMemberPaybacks">
      <payback-list-tile :key="payback.debtor + '_' + payback.creditor"
                         :payback="payback"
                         :divider="idx < otherMemberPaybacks.length - 1">
      </payback-list-tile>
    </template>
  </v-list>
</div>

</template>

<script>

import _ from 'lodash'

import collectiveStats from '@/mixins/collectiveStats'
import selectedMember from '@/mixins/selectedMember'

import PaybackListTile from '@/components/PaybackListTile'

export default {
  name: 'cashing-up',
  mixins: [
    collectiveStats,
    selectedMember,
  ],
  components: {
    PaybackListTile,
  },
  data() {
    return {

    }
  },
  computed: {
    paybacks() {
      if (!this.collective) {
        return []
      }
      return this.collective.stats.cashup
    },
    /**
     * Ignore unwieldy peanut paybacks.
     */
    sanitizedPaybacks() {
      return this.paybacks.filter(payback => {
        return Math.abs(payback.amount) > 0.01
      })
    },
    /**
     * Sorted by amount.
     */
    sortedPaybacks() {
      return _.orderBy(this.sanitizedPaybacks, 'amount', 'desc')
    },
    selectedMemberPaybacks() {
      return this.sortedPaybacks.filter(payback => {
        return this.isSelectedMemberPayback(payback)
      })
    },
    otherMemberPaybacks() {
      return this.sortedPaybacks.filter(payback => {
        return !this.isSelectedMemberPayback(payback)
      })
    },
  },
  methods: {
    isSelectedMemberPayback(payback) {
      return (payback.debtor === this.selectedMember.id ||
              payback.creditor === this.selectedMember.id)
    },
  },
}

</script>

<style scoped>

</style>