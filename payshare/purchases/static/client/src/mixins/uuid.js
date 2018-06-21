export default {
  computed: {
    uuid() {
      const key = this.$route.params.key
      return this.isUUID(key) ? key : null
    }
  },
  methods: {
    isUUID(key) {
      const pattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
      return pattern.test(key)
    },
  },
}
