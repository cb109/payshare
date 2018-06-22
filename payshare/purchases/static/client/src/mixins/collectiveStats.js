export default {
  computed: {
    collective() {
      return this.$store.state.collective
    },
    overallPurchased() {
      if (!this.collective) {
        return 0
      }
      return Number(this.collective.stats.overall_purchased).toFixed(2)
    },
    overallDebt() {
      if (!this.collective) {
        return 0
      }
      return Number(this.collective.stats.overall_debt).toFixed(2)
    },
    numPurchases() {
      if (!this.collective) {
        return 0
      }
      return this.collective.stats.num_purchases
    },
    numLiquidations() {
      if (!this.collective) {
        return 0
      }
      return this.collective.stats.num_liquidations
    },
    averagePurchasePrice() {
      if (!this.collective) {
        return 0
      }
      return Number(this.overallPurchased / this.numPurchases).toFixed(2)
    },
    averageLiquidationAmount() {
      if (!this.collective) {
        return 0
      }
      return Number(this.overallDebt / this.numLiquidations).toFixed(2)
    },
  },
}
