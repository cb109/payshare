<template>

<div>
  <v-card class="my-2">
    <v-card-text class="px-2 pt-2 pb-0">
      <v-layout row
                align-center>
        <v-layout v-bind="layout"
                  align-center
                  justify-center
                  class="no-grow mr-2 mb-2">
          <div v-if="creditor.avatar"
               class="avatar">
            <img :src="creditor.avatar"
                 class="avatar">
          </div>
          <v-icon class="pa-0 liquidation-arrow"
                  v-if="$vuetify.breakpoint.smAndUp">
            arrow_right
          </v-icon>
          <v-icon class="pa-0 liquidation-arrow"
                  v-else>
            arrow_drop_down
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
              <strong :class="{'primary--text': isCreditor}">
                {{ creditor.username }}
              </strong>
              {{ $t('gaveMoneyTo') }}
              <strong :class="{'primary--text': isDebtor}">
                {{ debtor.username }}
              </strong>
              {{ $t('for') }} <br>
            </div>
            <div class="name">
              {{ liquidation.description }}
            </div>
          </div>
          <v-spacer></v-spacer>
          <v-layout column
                    :style="{'width': $vuetify.breakpoint.xsOnly ? '100%' : 'initial'}"
                    fill-height>
            <div class="text-xs-right">
              {{ createdAgo }}
            </div>
            <div class="pl-5 amount"
                 :class="{'secondary--text': !isCreditor && !isDebtor,
                          'red--text': isDebtor,
                          'green--text': isCreditor}">
              {{ amount }}
              <span class="currency">
                {{ $t(currency) }}
              </span>
            </div>
          </v-layout>
        </v-layout>
      </v-layout>
    </v-card-text>
  </v-card>
</div>

</template>

<script>

import moment from 'moment'

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
    createdAgo() {
      return moment(
        this.liquidation.created_at).locale(this.$i18n.locale).fromNow()
    },
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
      return this.liquidation.amount.currency
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
  max-height: 24px;
}

</style>