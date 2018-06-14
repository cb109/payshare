<template>

<div>
  <v-card class="my-2">
    <v-card-text class="px-2 pt-2 pb-0">
      <v-layout row
                align-center>
        <v-layout row
                  class="no-grow mr-3 mt-1 mb-4">
          <div v-if="creditor.avatar"
               class="avatar">
            <img :src="creditor.avatar"
                 class="avatar">
          </div>
          <v-icon class="pa-0 liquidation-arrow primary--text"
                  color="default">
            arrow_right
          </v-icon>
          <div v-if="debtor.avatar"
               class="avatar">
            <img :src="debtor.avatar"
                 class="avatar">
          </div>
        </v-layout>
        <v-layout v-bind="layout"
                  align-baseline
                  fill-height>
          <div class="text">
            <div class="description">
              <strong>{{ creditor.username }}</strong>
              {{ $t('gaveMoneyTo') }}
              {{ debtor.username }}
              {{ $t('for') }} <br>
            </div>
            <div class="name">
              {{ liquidation.description }}
            </div>
          </div>

          <v-spacer></v-spacer>
          <div class="pl-5 amount"
               :class="{'primary--text': !isCreditor && !isDebtor,
                        'red--text': isDebtor,
                        'green--text': isCreditor}">
            {{ amount }}
            <span class="currency">
              {{ currency }}
            </span>
          </div>
        </v-layout>
      </v-layout>
    </v-card-text>
  </v-card>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'

export default {
  mixins: [
    selectedMember,
  ],
  name: 'liquidation',
  props: {
    'liquidation': {
      type: Object,
      required: true,
    },
  },
  computed: {
    layout() {
      if (this.$vuetify.breakpoint.xsOnly) {
        return {column: true}
      }
      return {row: true}
    },
    creditor() {
      const member = this.collective.members.filter(
        user => user.id === this.liquidation.creditor)[0]
      return member
    },
    debtor() {
      const collective = this.$store.state.collective
      const member = collective.members.filter(
        user => user.id === this.liquidation.debtor)[0]
      return member
    },
    amount() {
      return Number(this.liquidation.amount.amount).toFixed(2)
    },
    currency() {
      const currency = this.liquidation.amount.currency
      return currency === 'EUR' ? '€' : currency
    },
    isCreditor() {
      if (!this.selectedMember) {
        return false
      }
      return this.selectedMember.id === this.creditor.id
    },
    isDebtor() {
      if (!this.selectedMember) {
        return false
      }
      return this.selectedMember.id === this.debtor.id
    },
  },
}

</script>

<style scoped>

.no-grow {
  flex-grow: 0;
}

.text {
  align-self: flex-start;
}

.description {
  font-size: 1.5em;
}

.name {
  font-size: 2.5em;
}

.amount {
  font-size: 3em;
  font-weight: bold;
  align-self: flex-end;
  white-space: nowrap;
}

.avatar {
  max-width: 72px;
  max-height: 72px;
}

@media (max-width: 599px) {
  .description {
    font-size: 1.15em;
  }

  .name {
    font-size: 1.5em;
  }

  .amount {
    font-size: 1.75em;
  }

  .avatar {
    max-width: 64px;
    max-height: 64px;
  }
}

.currency {
  opacity: 0.25;
}

.liquidation-arrow {
  font-size: 5em;
  max-width: 24px;
}

</style>