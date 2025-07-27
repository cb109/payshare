export function getFullUserName(user) {
  return (user.first_name || user.username) + ' ' + user.last_name;
}

export function getUserName(user) {
  return user.first_name || user.username;
}

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
      return users
    },
    selectedMember: {
      get() {
        return this.$store.state.selectedMember
      },
      set(member) {
        this.$store.commit('SET_SELECTED_MEMBER', member)
      },
    },
    selectedMemberBalance() {
      if (!this.collective || !this.selectedMember) {
        return 0
      }
      let balance = undefined
      this.collective.stats.sorted_balances.forEach(tuple => {
        const memberId = tuple[0]
        if (memberId == this.selectedMember.id) {
          balance = tuple[1]
          // Sanitize by ignoring unwieldy peanut values.
          if (Math.abs(balance) <= 0.01) {
            balance = 0
          }
          balance = Number(balance).toFixed(2)
          return
        }
      })
      return balance
    },
  },
  methods: {
    getFullUserName: getFullUserName,
    getUserName: getUserName,
    getMemberForId(id) {
      const candidates = this.members.filter(m => m.id === id)
      if (!candidates.length) {
        return null
      }
      return candidates[0]
    },
    rememberSelectedMember() {
      this.$store.commit('LOAD_SELECTED_MEMBER_FROM_LOCALSTORAGE')
    },
  },
}
