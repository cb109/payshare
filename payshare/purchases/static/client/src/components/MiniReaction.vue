<template>

<div @click="expanded = !expanded"
     class="clickable"
     :title="username">
  <v-layout align-center>
    <img src="/static/img/mozilla-heavy-black-heart.png"
         width="20"
         v-if="reaction.meaning === 'positive'">
    <img src="/static/img/mozilla-expressionless-face.png"
         width="20"
         v-if="reaction.meaning === 'neutral'">
    <img src="/static/img/mozilla-pile-of-poo.png"
         width="20"
         v-if="reaction.meaning === 'negative'">
    <div v-if="expanded"
         class="ml-1 caption">
      {{ username }}
    </div>
  </v-layout>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'

export default {
  name: 'mini-reaction',
  mixins: [
    selectedMember,
  ],
  props: {
    'reaction': {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      expanded: false
    }
  },
  computed: {
    username() {
      return this.getMemberForId(this.reaction.member).username
    },
  },
}

</script>
