export default {
  computed: {
    isDialogActive() {
      return this.$store.state.dialogActive
    },
  },
  mounted() {
    this.$bus.$on('dialog-active', active => {
      this.$store.commit('SET_DIALOG_ACTIVE', active)
    })
  },
  methods: {
    closeAllDialogs() {
      this.$bus.$emit('close-all-dialogs')
    },
    handleRouteChange(to, from, next) {
      if (this.isDialogActive) {
        this.closeAllDialogs()
        return next(false)
      }
      next()
    },
  },
  beforeRouteUpdate(to, from, next) {
    return this.handleRouteChange(to, from, next)
  },
  beforeRouteLeave(to, from, next) {
    return this.handleRouteChange(to, from, next)
  },
}
