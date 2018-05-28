<template>

<div>
  <v-card class="my-2">
    <v-card-text class="pb-0">
      <v-layout justify-space-between
                align-baseline
                fill-height>
        <div class="text">
          <div class="description">
            {{ buyerName }} {{ $t('payedFor') }} <br>
          </div>
          <div class="name">
            {{ purchase.name }}
            </div>
        </div>
        <div class="pl-5 price primary--text">
          {{ price }}
          {{ currency }}
        </div>
      </v-layout>
    </v-card-text>
  </v-card>
</div>

</template>

<script>

export default {
  name: 'purchase',
  props: {
    'purchase': {
      type: Object,
      required: true,
    },
  },
  computed: {
    buyerName() {
      const collective = this.$store.state.collective
      const member = collective.members.filter(
        user => user.id === this.purchase.buyer)[0]
      return member.username
    },
    price() {
      return Number(this.purchase.price.amount).toFixed(2)
    },
    currency() {
      const currency = this.purchase.price.currency
      return currency === 'EUR' ? '€' : currency
    },
  },
}

</script>

<style scoped>

.text {
  align-self: flex-start;
}

.description {
  font-size: 2em;
}

.name {
  font-size: 3em;
}

.price {
  font-size: 6em;
  font-weight: bold;
  align-self: flex-end;
  white-space: nowrap;
}

</style>