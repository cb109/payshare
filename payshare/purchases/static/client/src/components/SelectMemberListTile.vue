<template>

<div v-if="members">
  <v-list-tile>
    <v-list-tile-action>
      <v-avatar v-if="member">
        <img :src="member.avatar"
            style="position: relative; left: -12px">
      </v-avatar>
      <v-icon v-else>
        person
      </v-icon>
    </v-list-tile-action>
    <v-list-tile-content>
      <v-select
        :label="label"
        :value="member"
        @input="((user) => $emit('update:member', user))"
        :items="members"
        item-value="id"
        :item-text="getFullUserName"
        hide-details
        return-object
        style="width: 100%"
      >
        <template slot="item"
                  slot-scope="data">
          <v-list-tile-avatar>
            <img :src="data.item.avatar">
          </v-list-tile-avatar>
          <v-list-tile-content>
            <v-list-tile-title>
              {{ getUserName(data.item) }}
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
import { getUserName, getFullUserName } from '@/mixins/selectedMember'

export default {
  name: 'select-member-list-tile',
  props: {
    label: {
      type: String,
      required: true,
    },
    member: {
      type: null|Object,
      required: true,
    },
    members: {
      type: Array[Object],
      required: true,
    },
  },
  methods: {
    getFullUserName: getFullUserName,
    getUserName: getUserName,
  }
}

</script>
