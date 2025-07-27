export default {
  methods: {
    softdelete(displayName, transfer) {
      const confirmed = confirm('"' + displayName + '" - ' +
                                this.$t('confirmDeleteTransfer'))
      if (!confirmed) {
        return;
      }
      return this.$store.dispatch('DELETE_TRANSFER', {
        kind: transfer.kind,
        id: transfer.id,
      })
    }
  },
}
