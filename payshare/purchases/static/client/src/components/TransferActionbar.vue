<template>

<div>
  <v-layout align-center
            wrap>
    <div v-for="(reaction, reactionIdx) in transfer.reactions"
         :key="reactionIdx"
         class="mb-1">
      <v-layout align-center>
        <mini-reaction
          :reaction="reaction"
          :initially-expanded="usernamesInitiallyExpanded"
        ></mini-reaction>
      </v-layout>
    </div>
    <v-layout
      v-if="allowEdit"
      nowrap
    >
      <v-spacer></v-spacer>
      <reaction-menu
        v-if="selectedMember"
        class="mr-1"
        :member="selectedMember"
        :transfer="transfer"
      ></reaction-menu>
      <v-btn icon
             small
             class="ma-0 mr-1"
             @click="edit(transfer)">
        <v-icon color="grey lighten-1">
          edit
        </v-icon>
      </v-btn>
      <v-btn icon
             small
            class="ma-0"
             @click="softdelete(transfer.name, transfer)">
        <v-icon color="grey lighten-1">
          delete
        </v-icon>
      </v-btn>
    </v-layout>
  </v-layout>
</div>

</template>

<script>

import edit from '@/mixins/edit'
import selectedMember from '@/mixins/selectedMember'
import softdelete from '@/mixins/softdelete'

import MiniReaction from '@/components/MiniReaction'
import ReactionMenu from '@/components/ReactionMenu'

export default {
  name: 'transfer-actionbar',
  mixins: [
    edit,
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
    'allowEdit': {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      expanded: false
    }
  },
  computed: {
    usernamesInitiallyExpanded() {
      return (this.$vuetify.breakpoint.mdAndUp ||
              this.transfer.reactions.length < 8)
    }
  },
}

</script>
