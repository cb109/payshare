export default {
  methods: {
    edit(transfer) {
      this.$bus.$emit('edit-transfer-in-dialog', transfer)
    }
  },
}
