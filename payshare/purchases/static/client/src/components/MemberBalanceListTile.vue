<template>

<div>
  <v-list-tile :value="highlight">
    <v-list-tile-action>
    <v-avatar v-if="member && member.avatar"
              class="small">
      <img :src="member.avatar">
    </v-avatar>
      <v-icon v-else>
        person
      </v-icon>
    </v-list-tile-action>
    <v-list-tile-content>
      <v-list-tile-title>
        {{ member.first_name || member.username }}
      </v-list-tile-title>
    </v-list-tile-content>
    <v-list-tile-action
      class="title"
      :class="{'red--text': balance < 0,
               'default--text': balance == 0,
               'green--text': balance > 0}">
      {{ Number(balance).toFixed(2) }} {{ collective.currency_symbol }}
    </v-list-tile-action>
  </v-list-tile>
</div>

</template>

<script>

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
  },
}

</script>

<style>

.small.avatar {
  width: 36px !important;
  height: 36px !important;
}

</style>