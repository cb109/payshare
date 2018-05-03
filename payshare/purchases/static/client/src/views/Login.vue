<template>
  <v-container fluid>
    <v-slide-y-transition mode="out-in">
      <v-layout column
                d-block
                align-center>
        <v-text-field label="Password"
                      v-model="password"></v-text-field>
        <v-layout>
          <v-spacer></v-spacer>
          <v-btn @click="loginWithCredentials(uuid, password)">
            Login
          </v-btn>
        </v-layout>
      </v-layout>
    </v-slide-y-transition>
  </v-container>
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
    }
  },
  methods: {
    loginWithCredentials(uuid, password) {
      this.$store.dispatch('RETRIEVE_COLLECTIVE_USING_CREDENTIALS', {
        'uuid': uuid,
        'password': password,
      }).then(() => {
        this.password = null
        this.$router.push('/transfers')
      })
    },
  },
}

</script>