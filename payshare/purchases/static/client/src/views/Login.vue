<template>

<v-layout column
          align-center>
  <v-flex xs12>
    <v-text-field
      ref="password"
      label="Password"
      type="password"
      v-model="password"
      @keyup.native.enter="loginWithCredentials(uuid, password)"
      @keyup.native.esc="password = null"
      :error="failed"
      :error-messages="errorMessages">
    </v-text-field>
    <v-btn @click="loginWithCredentials(uuid, password)"
           :loading="loading"
           style="align-self: flex-end">
      Login
    </v-btn>
  </v-flex>
</v-layout>

</template>

<script>

import uuid from '@/mixins/uuid'

export default {
  name: 'Login',
  mixins: [
    uuid,
  ],
  data() {
    return {
      password: null,
      loading: false,
      failed: false,
      errorMessages: [],
    }
  },
  methods: {
    loginWithCredentials(uuid, password) {
      this.loading = true
      this.$store.dispatch('RETRIEVE_COLLECTIVE_USING_CREDENTIALS', {
        'uuid': uuid,
        'password': password,
      })
      .then(() => {
        this.loading = false
        this.failed = false
        this.errorMessages = []

        this.password = null
        this.$router.push('/transfers')
      })
      .catch(error => {
        this.loading = false
        this.failed = true
        this.errorMessages = [error.response.data.detail]
      })
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.$refs.password ? this.$refs.password.focus() : null
    })
  },
}

</script>