<template>

<div v-if="collective && members">
  <v-dialog :fullscreen="$vuetify.breakpoint.xsOnly"
            max-width="480px"
            :persistent="loading"
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
          required
          type="number"
          v-model="price"
          append-icon="euro_symbol"
          :label="$t('price')"
          class="price"
        ></v-text-field>
        <v-text-field
          required
          :label="$t('name')"
          :placeholder="$t('placeholderPurchaseName')"
          v-model="name"
        ></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="error"
               flat
               @click="abort()">
          {{ $t('abort') }}
        </v-btn>
        <v-btn color="success"
               @click="confirm()"
               :flat="!formIsValid"
               :outline="formIsValid"
               :disabled="!formIsValid"
               :loading="loading">
          {{ $t('confirm') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</div>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'
import SelectMemberListTile from '@/components/SelectMemberListTile'

const defaults = {
  loading: false,

  // Form data.
  buyer: null,
  name: '',
  price: null,
}

export default {
  name: 'create-purchase-dialog',
  mixins: [
    selectedMember,
  ],
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
      ...defaults,
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
    formIsValid() {
      return (this.price > 0 &&
              this.name.trim().length > 2 &&
              this.buyer !== null)
    },
  },
  watch: {
    show: function(val) {
      if (val) {
        if (!this.buyer) {
          this.buyer = this.selectedMember
        }
      }
    },
  },
  methods: {
    confirm() {
      this.loading = true
      this.$store.dispatch('CREATE_PURCHASE', {
        buyerId: this.buyer.id,
        price: this.price,
        name: this.name,
      }).then(() => {
        this.abort()
      }).catch(() => {
        this.loading = false
      })
    },
    abort() {
      this.showDialog = false
      this.reset()
    },
    reset() {
      Object.keys(defaults).forEach(key => {
        const val = defaults[key]
        this[key] = val
      })
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