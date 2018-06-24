<template>

<v-list v-if="selectedMember && sortedBalanceObjects">
  <v-list-tile slot="activator">
    <v-list-tile-action>
      <v-icon>account_balance</v-icon>
    </v-list-tile-action>
    <v-list-tile-content>
      <v-list-tile-title>
        {{ $t('financialStatus') }}
      </v-list-tile-title>
    </v-list-tile-content>
  </v-list-tile>
  <v-list-tile>
    <v-list-tile-content>
      <v-list-tile-sub-title>
        {{ $t('founded') }} {{ createdDateAgo }},
        {{ collective.members.length }} {{ $t('members') }}
      </v-list-tile-sub-title>
    </v-list-tile-content>
  </v-list-tile>
  <v-list-tile>
    <v-list-tile-content>
      <v-list-tile-title>
        {{ $t('overallPurchased') }}
      </v-list-tile-title>
      <v-list-tile-sub-title>
        {{ numPurchases }}
        ({{ $t('median') }}: {{ medianPurchasePrice }}
        {{ collective.currency_symbol }})
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action>
      {{ overallPurchased }}
      {{ collective.currency_symbol }}
    </v-list-tile-action>
  </v-list-tile>
  <v-list-tile>
    <v-list-tile-content>
      <v-list-tile-title>
        {{ $t('overallDebt') }}
      </v-list-tile-title>
      <v-list-tile-sub-title>
        {{ numLiquidations }}
        ({{ $t('median') }}: {{ medianLiquidationAmount }}
        {{ collective.currency_symbol }})
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action>
      {{ overallDebt }}
      {{ collective.currency_symbol }}
    </v-list-tile-action>
  </v-list-tile>
  <template v-for="(obj, idx) in sortedBalanceObjects">
    <member-balance-list-tile
      :key="obj.memberId"
      :member-id="obj.memberId"
      :highlight="obj.memberId === selectedMember.id"
      :balance="obj.balance"
    ></member-balance-list-tile>
    <v-divider v-if="idx < sortedBalanceObjects.length - 1"></v-divider>
  </template>
</v-list>

</template>

<script>

import collectiveStats from '@/mixins/collectiveStats'
import createdDate from '@/mixins/createdDate'
import selectedMember from '@/mixins/selectedMember'

import MemberBalanceListTile from '@/components/MemberBalanceListTile'

export default {
  name: 'ranking-list',
  mixins: [
    collectiveStats,
    createdDate,
    selectedMember,
  ],
  components: {
    MemberBalanceListTile,
  },
  data() {
    return {

    }
  },
  computed: {
    // FIXME: Reusing date mixin here, but the interface does not match
    //  this view. Refactor to make it more generic.
    transfer() {
      return this.collective
    },
    /**
     * Cast list of tuples to list objects with same ordering.
     */
    sortedBalanceObjects() {
      if (!this.collective) {
        return []
      }
      const objs = []
      const balances = this.collective.stats.sorted_balances
      for (var i = 0; i < balances.length; i++) {
        objs.push({
          memberId: balances[i][0],
          balance: balances[i][1],
        })
      }
      return objs
    },
  },
}

</script>

<style scoped>

.reaction-menu {

}

.reaction-btn {
  margin: 0;
  opacity: 0.35;
}

.reaction-icon-btn {
  min-width: 48px;
  height: auto;
}

</style>