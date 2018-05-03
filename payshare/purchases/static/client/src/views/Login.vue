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

export default {
  name: 'Login',
  data() {
    return {
      password: null,
    }
  },
  // FIXME: move uuid and isUUID to a mixin to use in multiple views
  computed:{
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
    loginWithCredentials(uuid, password) {
      this.$store.dispatch('RETRIEVE_COLLECTIVE_USING_CREDENTIALS', {
        'uuid': uuid,
        'password': password,
      }).then(() => this.password = null)
    },
  },
}

</script>