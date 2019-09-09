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
            <v-layout align-center>
              <v-icon v-if="isCreateAction">add</v-icon>
              <v-icon v-if="isUpdateAction">edit</v-icon>
              <span class="m-2">
                {{ headline }}
              </span>
            </v-layout>
          </h3>
        </v-toolbar-title>
      </v-toolbar>
      <v-toolbar flat
                 dense
                 color="primary"
                 v-show="action === 'create'">
        <v-btn-toggle v-model="mode"
                      mandatory
                      class="elevation-0"
                      style="width: 100%">
          <v-btn flat
                 block
                 color="white"
                 style="height: 48px"
                 value="purchase">
            <span class="black--text">
              {{ $t('purchase') }}
            </span>
          </v-btn>
          <v-btn flat
                 block
                 color="white"
                 style="height: 48px"
                 value="liquidation">
            <span class="black--text">
              {{ $t('liquidation') }}
            </span>
          </v-btn>
        </v-btn-toggle>
      </v-toolbar>
      <v-card-actions class="mt-2">
        <v-layout justify-center>
          <v-btn color="error"
                 block
                 flat
                 @click="abort()">
            {{ $t('abort') }}
          </v-btn>
          <v-btn color="success"
                 block
                 @click="confirm()"
                 :disabled="!formIsValid"
                 :loading="loading">
            {{ confirmButtonTitle }}
          </v-btn>
        </v-layout>
      </v-card-actions>
      <v-card-text>
        <h4 class="subheading mb-2">{{ explanation }}</h4>
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
        <v-layout justify-end>
          <v-btn v-if="isLiquidationMode && (creditor || debtor)"
                 fab
                 small
                 absolute
                 style="right: 8px"
                 :style="{'top': swapButtonTopOffset}"
                 @click="swapCreditorAndDebtor()">
            <v-icon medium>swap_vert</v-icon>
          </v-btn>
        </v-layout>
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
      return this.isCreateAction ? this.$t('confirm') : this.$t('save')
    },
    swapButtonTopOffset() {
      if (this.isCreateAction) {
        return this.$vuetify.breakpoint.xsOnly ? '310px' : '292px'
      }
      else {
        return this.$vuetify.breakpoint.xsOnly ? '260px' : '242px'
      }
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
        return (this.price > 0 &&
                this.name.trim().length > 0 &&
                this.buyer !== null)
      }
      else if (this.isLiquidationMode) {
        return (this.price > 0 &&
                this.name.trim().length > 0 &&
                this.creditor !== null &&
                this.debtor !== null)
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
