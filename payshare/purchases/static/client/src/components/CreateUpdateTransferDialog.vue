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
          v-model="name"
          clearable
          counter="100"
          :rules="[((v) => !!v && v.length < 100 || $t('tooLong'))]"
          :label="$t('description')"
          :placeholder="$t('placeholderPurchaseName')"
        ></v-text-field>
        <v-text-field
          type="number"
          v-model="price"
          append-icon="euro_symbol"
          :label="$t('amount')"
          :placeholder="'59.99'"
          class="price"
        ></v-text-field>
        <div v-if="isPurchaseMode && isUpdateAction">
          <v-radio-group
            v-model="weightsExpanded"
            row
            mandatory
            hide-details
          >
            <v-radio
              :label="$t('weightsRadioOptionEven')"
              :value="false"
              color="grey"
            />
            <v-radio
              :label="$t('weightsRadioOptionDifferent')"
              :value="true"
              color="warning"
              :class="[weightsExpanded ? 'v-radio-label--warning' : '']"
            />
          </v-radio-group>
          <v-slide-y-transition>
            <div
              v-if="weightsExpanded"
              class="mt-3"
            >
              <table
                style="
                  width: 100%;
                  border-collapse: separate;
                  border-spacing: 0 4px;
                "
              >
                <thead>
                  <th class="px-2" style="text-align: left">
                    {{ $t('weightsTableHeaderWho') }}
                  </th>
                  <th class="px-2" style="text-align: left">
                    {{ $t('weightsTableHeaderShare') }}
                  </th>
                  <th class="px-2" style="text-align: left">
                    {{ collective.currency_symbol }}
                  </th>
                </thead>
                <tbody>
                  <tr
                    v-for="member in members"
                    :key="member.id"
                  >
                    <td class="px-2">
                      {{ getFullUserName(member) }}
                    </td>
                    <td class="px-2">
                      <v-text-field
                        :value="getPurchaseWeightForMemberId(member.id)"
                        @input="(weight) => setPurchaseWeightForMemberId(member.id, Number(weight))"
                        hide-details
                        type="number"
                        clearable
                        min="0"
                        max="100"
                        step="1"
                        class="pt-0 pb-2"
                        style="max-width: 140px"
                      ></v-text-field>
                    </td>
                    <td class="px-2" :key="weightsModifiedCounter">
                      {{ getPurchaseWeightPreviewForMember(transferToUpdate, member) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </v-slide-y-transition>
        </div>
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
  weightsExpanded: false,
  weightsModifiedCounter: 0,

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
      ...defaults
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
      return users.sort((u1, u2) => {
        return this.getFullUserName(u1) > this.getFullUserName(u2);
      })
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

        if (this.isUpdateAction && this.weightsExpanded) {
          const weights = this.getPurchaseUpdateWeights();
          if (weights.some(weight => isNaN(weight.weight))) {
            return false;
          }
        }

        return (
          this.price !== 0 &&
          this.name &&
          this.name.trim().length > 0 &&
          this.buyer !== null
        )
      }
      else if (this.isLiquidationMode) {
        return (
          this.price !== 0 &&
          this.name &&
          this.name.trim().length > 0 &&
          this.creditor !== null &&
          this.debtor !== null
        )
      }
    },
  },
  watch: {
    show: function(show) {
      this.$bus.$emit('dialog-active', show)

      if (show) {
        if (
          this.isPurchaseMode &&
          this.isUpdateAction &&
          this.transferToUpdate &&
          this.transferToUpdate.weights.length > 0
        ) {
          this.weightsExpanded = true;
        }

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
    getPurchaseWeightForMemberId(memberId) {
      if (
        this.isPurchaseMode &&
        this.isUpdateAction &&
        this.transferToUpdate &&
        this.transferToUpdate.weights.length > 0
      ) {
        const forMember = this.transferToUpdate.weights.filter(w => w.member == memberId)[0];
        if (forMember) {
          return forMember.weight;
        }
      }
      return 1;
    },
    setPurchaseWeightForMemberId(memberId, weight) {
      if (
        this.isPurchaseMode &&
        this.isUpdateAction &&
        this.transferToUpdate
      ) {
        const forMember = this.transferToUpdate.weights.filter(w => w.member == memberId)[0];
        if (forMember) {
          forMember.weight = weight;
        } else {
          if (!this.transferToUpdate.weights) {
            this.transferToUpdate.weights = [];
          }
          this.transferToUpdate.weights.push({
            member: memberId,
            weight: weight,
          });
        }
        this.weightsModifiedCounter += 1;
      }
    },
    getPurchaseWeightPreviewForMember(purchase, member) {
      if (!purchase) {
        return '';
      }
      const memberIdToWeight = {};
      for (const member_ of this.members) {
        memberIdToWeight[member_.id] = this.getPurchaseWeightForMemberId(member_.id);
      }
      const weights = Object.values(memberIdToWeight).filter(w => !isNaN(w));
      if (!weights.length) {
        return '';
      }
      const weightsSum = weights.reduce((a, b) => a + b);
      const perWeight = purchase.price.amount / weightsSum;
      const amount = memberIdToWeight[member.id] * perWeight;
      if (isNaN(amount)) {
        return '';
      }
      return amount.toFixed(2) + this.collective.currency_symbol;
    },
    getPurchaseUpdateWeights() {
      const weights = [];
      for (const member of this.members) {
        weights.push({
          member: member.id,
          weight: this.getPurchaseWeightForMemberId(member.id),
        });
      }
      return weights;
    },
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
      const payload = {
        id: this.transferToUpdate.id,
        buyerId: this.buyer.id,
        price: this.price,
        name: this.name,
      };

      if (this.weightsExpanded) {
        payload.weights = this.getPurchaseUpdateWeights();
      }

      this.$store.dispatch('UPDATE_PURCHASE', payload).then(() => {
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

.v-radio-label--warning .v-label {
  color: #fb8c00 !important;
}

.v-toolbar.toolbar--no-side-padding .v-toolbar__content {
  padding-left: 0;
  padding-right: 0;
}

</style>
