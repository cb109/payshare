<template>

<div class="my-1">
  <v-layout align-center
            wrap>
    <div v-for="(reaction, reactionIdx) in transfer.reactions"
         :key="reactionIdx">
      <v-layout align-center>
        <mini-reaction :reaction="reaction"></mini-reaction>
      </v-layout>
    </div>
    <v-spacer></v-spacer>
    <reaction-menu
      :member="selectedMember"
      :transfer="transfer"
    ></reaction-menu>
    <v-btn icon
           small
          class="ma-0"
           @click="softdelete(transfer.name, transfer)">
      <v-icon color="grey lighten-1">
        delete
      </v-icon>
    </v-btn>
  </v-layout>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'
import softdelete from '@/mixins/softdelete'

import MiniReaction from '@/components/MiniReaction'
import ReactionMenu from '@/components/ReactionMenu'

export default {
  name: 'transfer-actionbar',
  mixins: [
    selectedMember,
    softdelete,
  ],
  components: {
    MiniReaction,
    ReactionMenu,
  },
  props: {
    'transfer': {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      expanded: false
    }
  },
}

</script>
