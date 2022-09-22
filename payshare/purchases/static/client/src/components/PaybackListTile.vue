<template>

<div>
  <v-list-tile avatar
               :value="highlight"
               :style="{'background': highlight ? '#E8EAF6' : ' initial' }">
    <v-list-tile-avatar class="avatar-tile--small">
      <v-avatar>
        <img v-if="debtor.avatar"
             :src="debtor.avatar">
      </v-avatar>
    </v-list-tile-avatar>
    <v-list-tile-avatar class="avatar-tile--icon">
      <v-icon class="pa-0 payback-arrow grey--text">
        arrow_right
      </v-icon>
    </v-list-tile-avatar>
    <v-list-tile-avatar class="avatar-tile--small">
      <v-avatar>
        <img v-if="creditor.avatar"
             :src="creditor.avatar">
      </v-avatar>
    </v-list-tile-avatar>
    <v-spacer></v-spacer>
    <v-list-tile-action>
      <v-layout align-center>
        <div class="amount"
             :class="{'red--text': isDebtor,
                      'green--text': isCreditor}">
          {{ amount }}
          <span class="grey--text">{{ collective.currency_symbol }}</span>
        </div>
        <v-layout>
          <v-btn
            v-if="isDebtor && creditor.paypal_me_username"
            icon
            class="ml-3"
            :title="$t('paypalMeHint')"
            @click="openPaypalMePage(creditor.paypal_me_username, amount)"
          >
            <img
              src="/static/paypal_logo.png"
              alt="Paypal Me"
              width="24"
              height="24"
            />
          </v-btn>
        </v-layout>
      </v-layout>
    </v-list-tile-action>
  </v-list-tile>
  <v-list-tile :value="highlight"
               :style="{'background': highlight ? '#E8EAF6' : ' initial' }">
    <v-list-tile-content>
      <v-list-tile-title class="auto-height list__tile__title--wrap">
        <v-layout
          wrap
          align-center
        >
          <div>
            <strong :class="{'primary--text': isDebtor}">{{ debtor.username }}</strong>
            {{ $t('pays') }}&nbsp;
          </div>
          <div>
            {{ $t('to') }}<strong :class="{'primary--text': isCreditor}">
              {{ creditor.username }}
            </strong>
          </div>
          <v-btn
            v-if="isDebtor"
            class="mr-0 mt-0 ml-auto"
            color="success""
            round
            small
            @click="addPaybackLiquidation(payback)"
          >
            <v-icon color="white" class="mr-1">check</v-icon>
            {{$t('markPaybackAsDone') }}
          </v-btn>
        </v-layout>
      </v-list-tile-title>
    </v-list-tile-content>
  </v-list-tile>
  <v-divider v-if="divider"></v-divider>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'

const PAYPAL_ME_BASE_URL = 'https://www.paypal.me'

export default {
  name: 'payback-list-tile',
  mixins: [
    selectedMember,
  ],
  props: {
    payback: {
      type: Object,
      required: true,
    },
    highlight: {
      type: Boolean,
      default: false,
    },
    divider: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    creditor() {
      return this.getMemberForId(this.payback.creditor)
    },
    debtor() {
      return this.getMemberForId(this.payback.debtor)
    },
    amount() {
      return Number(this.payback.amount).toFixed(2)
    },
    isDebtor() {
      return this.selectedMember.id === this.debtor.id
    },
    isCreditor() {
      return this.selectedMember.id === this.creditor.id
    },
  },
  methods: {
    openPaypalMePage(username, amount) {
      const url = `${PAYPAL_ME_BASE_URL}/${username}/${amount}`
      window.open(url, '_blank')
    },
    addPaybackLiquidation(payback) {
      this.$bus.$emit('switch-to-tab', 'feed')

      this.$store.dispatch('CREATE_LIQUIDATION', {
        creditorId: payback.debtor,
        debtorId: payback.creditor,
        amount: payback.amount,
        name: this.$t('payback'),
      }).then(() => {
        this.$bus.$emit('switch-to-tab', 'feed')
      })
    }
  },
}

</script>

<style scoped>

.avatar-tile--small {
  min-width: 36px;
  max-width: 36px;
}

.avatar-tile--icon {
  min-width: 34px;
  max-width: 34px;
}

.payback-arrow {
  font-size: 3em;
  max-width: 36px;
  max-height: 36px;
}

.amount {
  font-size: 1.5em;
  font-weight: bold;
  white-space: nowrap;
}

</style>
