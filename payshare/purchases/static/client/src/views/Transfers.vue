<template>

<div>
  Transfers
  <div v-for="(transfer, transferIndex) in transfers"
      :key="transferIndex">
    {{ transfer.created_at }}
    {{ transfer.name }}
  </div>
</div>

</template>

<script>

export default {
  name: 'Transfers',
  data() {
    return {

    }
  },
  computed: {
    transfers() {
      return this.$store.state.transfers
    },
  },
  mounted() {
    this.$store.dispatch('LIST_TRANSFERS')
  },
}

</script>