<template>

<v-container>
  <v-layout column
            align-center
            justify-center>
    <v-layout justify-center
              class="mb-3 min-100">
      <img src="/static/img/payroll.png">
    </v-layout>
    <v-flex xs12>
      <v-text-field
        class="password-input"
        ref="password"
        :label="$t('password')"
        type="password"
        v-model="password"
        @keyup.native.enter="loginWithCredentials(uuid, password)"
        @keyup.native.esc="password = null"
        :error="failed"
        :error-messages="errorMessages">
      </v-text-field>
      <v-btn
        block
        color="primary"
        class="elevation-0"
        :loading="loading"
        @click="loginWithCredentials(uuid, password)"
      >
        {{ $t('login') }}
      </v-btn>
      <v-btn
        v-if="displayBackButton"
        block
        outline
        @click="$router.push('/unknown')"
      >
        {{ $t('back') }}
      </v-btn>
    </v-flex>
  </v-layout>
</v-container>

</template>

<script>

import selectedMember from '@/mixins/selectedMember'
import uuid from '@/mixins/uuid'

export default {
  mixins: [
    selectedMember,
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
  computed: {
    displayBackButton() {
      return this.$store.state.previousCollectiveKeys.length > 0
    },
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

        this.rememberSelectedMember()
        this.$bus.$emit('logged-in')

        this.password = null
        this.$router.push(`/${this.uuid}/transfers`)
      })
      .catch(error => {
        this.loading = false
        this.failed = true
        this.errorMessages = [this.$t(error.response.data.detail)]
      })
    },
  },
  created() {
    this.$store.commit('LOAD_PREVIOUS_COLLECTIVE_KEYS_FROM_LOCALSTORAGE')
  },
  mounted() {
    this.$nextTick(() => {
      this.$refs.password ? this.$refs.password.focus() : null
    })
  },
}

</script>

<style scoped>

.password-input {
  width: 200px;
}

.min-100 {
  min-width: 100px;
  min-height: 100px;
}

</style>