<template>

<div v-if="collective && members">
  <v-dialog
    v-model="showDialog"
    max-width="480px"
    persistent
    :fullscreen="$vuetify.breakpoint.xsOnly"
  >
    <v-card>
      <v-toolbar
        v-show="action === 'create'"
        flat
        dense
        class="toolbar--no-side-padding"
      >
        <v-btn
          flat
          block
          style="height: 56px"
          @click="mode = 'purchase'"
          :class="{'white black--text': isPurchaseMode,
                   'grey lighten-2 grey--text': isLiquidationMode}"
        >
          {{ $t('purchase') }}
        </v-btn>
        <v-btn
          flat
          block
          style="height: 56px"
          @click="mode = 'liquidation'"
          :class="{'white black--text': isLiquidationMode,
                   'grey lighten-2 grey--text': isPurchaseMode}"
        >
          {{ $t('liquidation') }}
        </v-btn>
      </v-toolbar>
      <v-card-text>
        <h3 class="headline mb-3">
          <v-layout
            align-center
            class="mt-1"
          >
            <v-icon
              v-if="isUpdateAction"
              class="mr-2"
            >
              edit
            </v-icon>
            <span>
              {{ headline }}
            </span>
          </v-layout>
        </h3>
        <v-layout align-center>
          <h4 class="subheading mb-2">
            {{ explanation }}
          </h4>
          <v-btn
            v-if="isLiquidationMode && (creditor || debtor)"
            small
            flat
            class="ml-auto my-0"
            @click="swapCreditorAndDebtor()"
          >
            <v-icon medium>
              swap_vert
            </v-icon>
          </v-btn>
        </v-layout>
        <select-member-list-tile
          v-if="isPurchaseMode"
          class="mb-4"
          :label="$t('buyer')"
          :members="members"
          :member.sync="buyer"
        ></select-member-list-tile>
        <select-member-list-tile
          v-if="isLiquidationMode"
          class="mb-4"
          :label="$t('creditor')"
          :members="membersMinusDebtor"
          :member.sync="creditor"
        ></select-member-list-tile>
        <select-member-list-tile
          v-if="isLiquidationMode"
          class="mb-4"
          :label="$t('debtor')"
          :members="membersMinusCreditor"
          :member.sync="debtor"
        ></select-member-list-tile>
        <v-text-field
          clearable
          counter="100"
          :rules="[((v) => v.length < 100 || $t('tooLong'))]"
          :label="$t('description')"
          :placeholder="$t('placeholderPurchaseName')"
          v-model="name"
        ></v-text-field>
        <v-text-field
          type="number"
          v-model="price"
          append-icon="euro_symbol"
          :label="$t('amount')"
          :placeholder="'59.99'"
          class="price"
        ></v-text-field>
      </v-card-text>
      <v-card-actions class="pb-3">
        <v-layout
          justify-center
          wrap
        >
          <v-btn
            color="error"
            block
            flat
            round
            @click="abort()"
          >
            {{ $t('abort') }}
          </v-btn>
          <v-btn
            color="success"
            block
            round
            class="elevation-0"
            :disabled="!formIsValid"
            :loading="loading"
            @click="confirm()"
          >
            {{ confirmButtonTitle }}
          </v-btn>
        </v-layout>
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

  // For purchase only.
  buyer: null,

  // For liquidation only.
  creditor: null,
  debtor: null,

  // Shared.
  name: '',
  price: null,

  // 'purchase' or 'liquidation'.
  mode: 'purchase',

  // 'create' or 'update'.
  action: 'create',
  transferToUpdate: null,
}

export default {
  name: 'create-update-transfer-dialog',
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
    confirmButtonTitle() {
      return this.isCreateAction ? this.$t('create') : this.$t('confirm')
    },
    isPurchaseMode() {
      return this.mode === 'purchase'
    },
    isLiquidationMode() {
      return this.mode === 'liquidation'
    },
    isCreateAction() {
      return this.action === 'create'
    },
    isUpdateAction() {
      return this.action === 'update'
    },
    headline() {
      return (this.isPurchaseMode
        ? (this.isCreateAction
           ? this.$t('addPurchase') : this.$t('editPurchase'))
        : (this.isCreateAction
           ? this.$t('addLiquidation') : this.$t('editLiquidation'))
      )
    },
    explanation() {
      return (this.isPurchaseMode
              ? this.$t('explainPurchase')
              : this.$t('explainLiquidation'))
    },
    collective() {
      return this.$store.state.collective
    },
    members() {
      const users = this.collective.members.concat()
      return users.sort((u1, u2) => u1.username > u2.username)
    },
    membersMinusCreditor() {
      if (!this.creditor) {
        return this.members
      }
      return this.members.filter(u => u.id !== this.creditor.id)
    },
    membersMinusDebtor() {
      if (!this.debtor) {
        return this.members
      }
      return this.members.filter(u => u.id !== this.debtor.id)
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
      if (this.isPurchaseMode) {
        return (
          this.price !== 0 &&
          this.name.trim().length > 0 &&
          this.buyer !== null
        )
      }
      else if (this.isLiquidationMode) {
        return (
          this.price !== 0 &&
          this.name.trim().length > 0 &&
          this.creditor !== null &&
          this.debtor !== null
        )
      }
    },
  },
  watch: {
    show: function(val) {
      this.$bus.$emit('dialog-active', val)

      if (val) {
        if (!this.buyer) {
          this.buyer = this.selectedMember
        }
        if (!this.creditor) {
          this.creditor = this.selectedMember

          // If there are only two members we can also preselect the debtor.
          if (this.members.length === 2) {
            const otherMember = this.members.filter(
              member => member.id !== this.creditor.id)[0]
            this.debtor = otherMember
          }
        }
      }
    },
  },
  methods: {
    setupSignals() {
      this.$bus.$on('edit-transfer-in-dialog', (transfer) => {
        this.action = 'update'
        this.mode = transfer.kind
        this.transferToUpdate = transfer

        this.name = transfer.name
        if (transfer.kind === 'purchase') {
          this.price = Number(transfer.price.amount).toFixed(2)
          this.buyer = this.getMemberForId(transfer.buyer)
        }
        else if (transfer.kind === 'liquidation') {
          this.price = Number(transfer.amount.amount).toFixed(2)
          this.creditor = this.getMemberForId(transfer.creditor)
          this.debtor = this.getMemberForId(transfer.debtor)
        }

        this.showDialog = true
      })

      this.$bus.$on('close-all-dialogs', () => {
        this.showDialog = false
      })
    },
    confirm() {
      if (this.isCreateAction) {
        if (this.isPurchaseMode) {
          this.createPurchase()
        }
        else if (this.isLiquidationMode) {
          this.createLiquidation()
        }
      }
      else if (this.isUpdateAction) {
        if (this.isPurchaseMode) {
          this.updatePurchase()
        }
        else if (this.isLiquidationMode) {
          this.updateLiquidation()
        }
      }
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
    createPurchase() {
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
    createLiquidation() {
      this.loading = true
      this.$store.dispatch('CREATE_LIQUIDATION', {
        creditorId: this.creditor.id,
        debtorId: this.debtor.id,
        amount: this.price,
        name: this.name,
      }).then(() => {
        this.abort()
      }).catch(() => {
        this.loading = false
      })
    },
    updatePurchase() {
      this.loading = true
      this.$store.dispatch('UPDATE_PURCHASE', {
        id: this.transferToUpdate.id,
        buyerId: this.buyer.id,
        price: this.price,
        name: this.name,
      }).then(() => {
        this.abort()
      }).catch(() => {
        this.loading = false
      })
    },
    updateLiquidation() {
      this.loading = true
      this.$store.dispatch('UPDATE_LIQUIDATION', {
        id: this.transferToUpdate.id,
        creditorId: this.creditor.id,
        debtorId: this.debtor.id,
        amount: this.price,
        name: this.name,
      }).then(() => {
        this.abort()
      }).catch(() => {
        this.loading = false
      })
    },
    swapCreditorAndDebtor() {
      const temp = this.creditor
      this.creditor = this.debtor
      this.debtor = temp
    },
  },
  created() {
    this.setupSignals()
  },
}

</script>

<style>

.v-toolbar.toolbar--no-side-padding .v-toolbar__content {
  padding-left: 0;
  padding-right: 0;
}

</style>
