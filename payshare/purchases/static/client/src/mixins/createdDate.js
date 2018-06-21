/**
 * Depends on: Must define a 'transfer' attribute.
 */
import moment from 'moment'

export default {
  data() {
    return {
      showAgoInsteadOfDate: true,
    }
  },
  computed: {
    createdDate_() {
      return moment(this.transfer.created_at).locale(this.$i18n.locale)
    },
    createdDateFormatted() {
      return this.createdDate_.format('DD.MM.YYYY, HH:mm');
    },
    createdDateAgo() {
      return this.createdDate_.fromNow()
    },
  },
  methods: {
    onCreatedDateClicked() {
      this.showAgoInsteadOfDate = !this.showAgoInsteadOfDate
    },
  },
}
