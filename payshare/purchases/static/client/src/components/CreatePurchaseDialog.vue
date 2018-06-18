<template>

<div>
  <v-dialog :fullscreen="$vuetify.breakpoint.xsOnly"
            max-width="480px"
            v-model="showDialog">
    <v-card>
      <v-toolbar flat
                 color="primary"
                 dark>
        <v-toolbar-title>
          <h3 class="headline">
            {{ $t('addPurchase') }}
          </h3>
        </v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <select-member-list-tile
          class="mb-2"
          :label="$t('buyer')"
          :members="members"
          :member.sync="buyer"
        ></select-member-list-tile>
        <v-text-field
          :label="$t('name')"
          v-model="name"
        ></v-text-field>
        <v-text-field
          type="number"
          v-model="price"
          append-icon="euro_symbol"
          :label="$t('price')"
          class="price"
        ></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error"
               flat
               @click="showDialog = false">
          {{ $t('abort') }}
        </v-btn>
        <v-btn color="success"
               outline>
          {{ $t('save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</div>

</template>

<script>

import SelectMemberListTile from '@/components/SelectMemberListTile'

export default {
  name: 'create-purchase-dialog',
  components: {
    SelectMemberListTile,
  },
  props: {
    show: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      buyer: null,
      name: '',
      price: 0.0,
    }
  },
  computed: {
    collective() {
      return this.$store.state.collective
    },
    members() {
      const users = this.collective.members.concat()
      return users.sort((u1, u2) => u1.username > u2.username)
    },
    showDialog: {
      get() {
        return this.show
      },
      set() {
        this.$emit('update:show', !this.show)
      },
    },
  },
}

</script>

<style scoped>

.price >>> .input-group__input input {
  height: auto;
  font-size: 3em;
  font-weight: bold;
}
.price >>> .input-group__input i {
  font-size: 3em;
}

.no-underline >>> .input-group__details::before {
  display: none;
}

</style>