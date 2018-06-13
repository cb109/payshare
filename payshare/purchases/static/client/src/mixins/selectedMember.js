export default {
  computed: {
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
