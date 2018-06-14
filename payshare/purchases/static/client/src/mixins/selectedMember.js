export default {
  computed: {
    collective() {
      return this.$store.state.collective
    },
    members() {
      if (!this.collective) {
        return []
      }
      const users = this.collective.members.concat()
      return users.sort((u1, u2) => u1.username > u2.username)
    },
    selectedMember: {
      get() {
        return this.$store.state.selectedMember
      },
      set(member) {
        this.$store.commit('SET_SELECTED_MEMBER', member)
      },
    },
  },
  methods: {
    rememberSelectedMember() {
      this.$store.commit('LOAD_SELECTED_MEMBER_FROM_LOCALSTORAGE')
    },
  },
}
