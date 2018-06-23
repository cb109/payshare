<template>

<v-menu left
        class="reaction-menu">
  <v-btn slot="activator"
         small
         flat
         icon
         class="reaction-btn">
    <img src="/static/img/lol.png"
         width="24">
  </v-btn>
  <v-list>
    <v-list-tile @click="addReactionToTransfer(member, transfer, 'positive')"
                class="mb-2">
      <img src="/static/img/mozilla-heavy-black-heart.png"
           width="48">
    </v-list-tile>
    <v-list-tile @click="addReactionToTransfer(member, transfer, 'neutral')"
                class="mb-2">
      <img src="/static/img/mozilla-expressionless-face.png"
           width="48">
    </v-list-tile>
    <v-list-tile @click="addReactionToTransfer(member, transfer, 'negative')">
      <img src="/static/img/mozilla-pile-of-poo.png"
           width="48">
    </v-list-tile>
  </v-list>
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
    addReactionToTransfer(member, transfer, reactionType) {
      console.log(member.username, reactionType, transfer.name);
    }
  },
}

</script>

<style scoped>

.reaction-menu {
  margin-left: auto;
  margin-right: 0;
  margin-top: 0;
  opacity: 0.5;
}

.reaction-btn {
  margin: 0;
  margin-bottom: 4px;
  opacity: 0.5;
}

</style>