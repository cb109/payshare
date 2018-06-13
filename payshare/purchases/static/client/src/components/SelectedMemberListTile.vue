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
        :label="$t('whoAreYou')"
        v-model="selectedMember"
        :items="members"
        item-value="id"
        item-text="username"
        return-object>
        <template slot="item"
                  slot-scope="data">
          <v-list-tile-avatar>
            <img :src="data.item.avatar">
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>
              {{ data.item.first_name || data.item.username }}
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
  watch: {
    selectedMember: function(val) {
      this.$emit('selected', val)
    }
  },
}

</script>