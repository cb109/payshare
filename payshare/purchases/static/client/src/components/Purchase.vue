<template>

<div>
  <v-card class="my-2">
    <v-card-text class="px-2 pt-2 pb-0">
      <v-layout row
                align-center>
        <div v-if="buyer.avatar"
             class="avatar mr-2 mb-2">
          <img :src="buyer.avatar"
               class="avatar">
        </div>
        <v-layout v-bind="layout"
                  align-baseline
                  fill-height>
          <div class="text">
            <div class="description">
              <strong :class="{'primary--text': isBuyer}">
                {{ buyer.username }}
              </strong>
              {{ $t('payedFor') }} <br>
            </div>
            <div class="name">
              {{ purchase.name }}
            </div>
          </div>
          <v-spacer></v-spacer>
          <v-layout column
                    :style="{'width': $vuetify.breakpoint.xsOnly ? '100%' : initial}"
                    fill-height>
            <div class="text-xs-right">
              {{ createdAgo }}
            </div>
            <div class="pl-5 price default--text">
              {{ price }}
              <span class="currency">
                {{ currency }}
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
  name: 'purchase',
  mixins: [
    selectedMember,
  ],
  props: {
    'purchase': {
      type: Object,
      required: true,
    },
  },
  computed: {
    createdAgo() {
      return moment(
        this.purchase.created_at).locale(this.$i18n.locale).fromNow()
    },
    layout() {
      if (this.$vuetify.breakpoint.xsOnly) {
        return {column: true}
      }
      return {row: true}
    },
    collective() {
      return this.$store.state.collective
    },
    buyer() {
      const member = this.collective.members.filter(
        user => user.id === this.purchase.buyer)[0]
      return member
    },
    price() {
      return Number(this.purchase.price.amount).toFixed(2)
    },
    currency() {
      const currency = this.purchase.price.currency
      return currency === 'EUR' ? '€' : currency
    },
    isBuyer() {
      if (!this.selectedMember) {
        return false
      }
      return this.selectedMember.id === this.buyer.id
    },
  },
}

</script>

<style scoped>

.text {
  align-self: flex-start;
}

.description {
  font-size: 1.5em;
}

.name {
  font-size: 2.5em;
}

.price {
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

  .price {
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

</style>