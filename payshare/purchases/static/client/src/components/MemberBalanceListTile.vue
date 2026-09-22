<template>

<div v-if="member">
  <v-list-tile :value="highlight"
               :style="{'background': highlight ? '#E8EAF6' : ' initial' }"
               avatar>
    <v-list-tile-avatar>
      <v-avatar>
        <img v-if="member.avatar"
             :src="member.avatar">
        <v-icon v-else>
          person
        </v-icon>
      </v-avatar>
    </v-list-tile-avatar>
    <v-list-tile-content>
      <v-list-tile-title class="list__tile__title--wrap">
        {{ getUserName(member) }}
      </v-list-tile-title>
      <v-list-tile-sub-title>
        {{ member.last_name || '' }}
      </v-list-tile-sub-title>
    </v-list-tile-content>
    <v-list-tile-action
      class="subheading"
      :class="{'red--text': sanitizedBalance < 0,
               'default--text': sanitizedBalance == 0,
               'green--text': sanitizedBalance > 0}">
      {{ Number(sanitizedBalance).toFixed(2) }}
      {{ collective.currency_symbol }}
    </v-list-tile-action>
  </v-list-tile>
</div>

</template>

<script>

import { getUserName } from '@/mixins/selectedMember'

export default {
  name: 'member-balance-list-tile',
  props: {
    memberId: {
      type: Number,
      required: true,
    },
    highlight: {
      type: Boolean,
      default: false,
    },
    balance: {
      type: Number,
      required: true,
    },
  },
  computed: {
    collective() {
      return this.$store.state.collective
    },
    members() {
      if (!this.collective) {
        return []
      }
      const users = this.collective.members.concat()
      return users.sort((u1, u2) => u1.username > u2.username)
    },
    member() {
      for (var i = this.members.length - 1; i >= 0; i--) {
        const member = this.members[i]
        if (member.id === this.memberId) {
          return member
        }
      }
    },
    sanitizedBalance() {
      let balance = this.balance
      // Ignore unwieldy peanut values.
      if (Math.abs(balance) <= 0.01) {
        balance = 0
      }
      return balance
    },
  },
  methods: {
    getUserName: getUserName,
  }
}

</script>
