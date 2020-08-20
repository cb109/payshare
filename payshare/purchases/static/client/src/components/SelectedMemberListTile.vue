<template>

<div v-if="members">
  <v-list-tile>
    <v-list-tile-action>
    <v-avatar v-if="selectedMember">
      <img :src="selectedMember.avatar"
           style="position: relative; left: -12px">
    </v-avatar>
      <v-icon v-else>
        person
      </v-icon>
    </v-list-tile-action>
    <v-list-tile-content>
      <v-select
        :label="label"
        v-model="selectedMember"
        :items="sortedMembers"
        item-value="id"
        item-text="username"
        hide-details
        return-object>
        <template slot="item"
                  slot-scope="data">
          <v-list-tile-avatar>
            <img :src="data.item.avatar">
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>
              {{ data.item.username }}
            </v-list-tile-title>
            <v-list-tile-sub-title>
              {{ data.item.last_name || '' }}
            </v-list-tile-sub-title>
          </v-list-tile-content>
        </template>
      </v-select>
    </v-list-tile-content>
  </v-list-tile>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'

export default {
  name: 'selected-member-list-tile',
  mixins: [
    selectedMember,
  ],
  props: {
    label: {
      type: String,
      required: true,
    },
  },
  computed: {
    /**
     * Members come in sorted alhpabetically, but we want the current
     * selected member to be on top to avoid changing it by accident.
     */
    sortedMembers() {
      if (!this.selectedMember) {
        return this.members
      }
      let members = this.members
      const memberIds = this.members.map(m => m.id)
      const idx = memberIds.indexOf(this.selectedMember.id)
      if (idx !== -1) {
        const selMember = this.members[idx]
        const rest = this.members.filter(m => m.id !== selMember.id)
        members = [selMember].concat(rest)
      }
      return members
    },
  },
  watch: {
    selectedMember: function(val) {
      this.$emit('selected', val)
    }
  },
}

</script>
