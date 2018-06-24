<template>

<v-menu left
        class="reaction-menu">
  <v-btn slot="activator"
         small
         flat
         icon
         class="reaction-btn">
    <img src="/static/img/lol.png"
         width="20">
  </v-btn>
  <v-card>
    <v-layout>
      <v-btn @click="addReactionToTransfer(member, transfer, 'negative')"
             flat
             class="reaction-icon-btn">
        <img src="/static/img/mozilla-pile-of-poo.png"
             width="48">
      </v-btn>
      <v-btn @click="addReactionToTransfer(member, transfer, 'neutral')"
             flat
             class="reaction-icon-btn">
        <img src="/static/img/mozilla-expressionless-face.png"
             width="48">
      </v-btn>
      <v-btn @click="addReactionToTransfer(member, transfer, 'positive')"
             flat
             class="reaction-icon-btn">
        <img src="/static/img/mozilla-heavy-black-heart.png"
             width="48">
      </v-btn>
    </v-layout>
  </v-card>
</v-menu>

</template>

<script>

export default {
  name: 'reaction-menu',
  props: {
    'member': {
      type: Object,
      required: true,
    },
    'transfer': {
      type: Object,
      required: true,
    }
  },
  methods: {
    addReactionToTransfer(member, transfer, meaning) {
      const opts = {
        memberId: member.id,
        transfer: transfer,
        meaning: meaning,
      }
      this.$store.dispatch('CREATE_REACTION', opts)
    }
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