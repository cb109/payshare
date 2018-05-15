<template>
  <v-app :dark="dark">
    <v-navigation-drawer app
                         fixed
                         clipped
                         v-model="drawer"
                         v-if="$store.getters.isLoggedIn">
      <v-layout column
                fill-height>
        <v-list>
          <v-list-tile @click=""
                       v-for="(menuItem, i) in menuItems"
                       :key="i">
            <v-list-tile-action>
              <v-icon>
                {{ menuItem.icon }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                {{ menuItem.title }}
                </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
        <v-spacer></v-spacer>
        <!-- Logout -->
        <v-list>
          <v-list-tile @click="logout()">
            <v-list-tile-action>
              <v-icon>
                exit_to_app
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                Logout
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </v-layout>
    </v-navigation-drawer>
    <v-toolbar app
               fixed
               clipped-left>
      <v-toolbar-side-icon
        v-if="$store.getters.isLoggedIn"
        @click.stop="drawer = !drawer">
      </v-toolbar-side-icon>
      <v-toolbar-title>
        <span v-if="!$store.getters.isLoggedIn">
          {{ title }}<span v-if="uuid">: {{ uuid }}</span>
        </span>
        <span v-else>
          {{ $store.state.collective.name }}
        </span>
        </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="$store.getters.isLoggedIn"
             @click="logout()"
             icon>
        <v-icon>exit_to_app</v-icon>
      </v-btn>
    </v-toolbar>
    <v-content>
      <v-container>
        <v-slide-y-transition mode="out-in">
          <router-view />
        </v-slide-y-transition>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>

import uuid from '@/mixins/uuid'

export default {
  name: 'App',
  mixins: [
    uuid,
  ],
  data () {
    return {
      drawer: false,
      dark: false,
      title: 'Payshare',
      menuItems: [
        {
          icon: 'add',
          title: 'Add Purchase',
        },
      ]
    }
  },
  methods: {
    setInitialDrawerState() {
      if (this.$vuetify.breakpoint.lgAndUp) {
        this.drawer = true
      }
    },
    checkUrl() {
      if (!this.uuid) {
        this.$router.push('/unknown')
      }
    },
    rememberCollective() {
      this.$store.commit('LOAD_COLLECTIVE_FROM_LOCALSTORAGE')
      if (this.$store.getters.isLoggedIn) {
        this.$router.push('/transfers')
      }
    },
    logout() {
      const key = this.$store.state.collective.key
      this.$store.commit('UNSET_COLLECTIVE')
      this.$router.push('/' + key)
    },
  },
  // FIXME: Dehydration of state races with created() and mounted() in
  //   other components and should better be handled explcitly, maybe
  //   using something like vuex-localstorage.
  created() {
    this.checkUrl()
    this.rememberCollective()
  },
  mounted() {
    this.setInitialDrawerState()
  },
}
</script>

<style>

.navigation-drawer {
  padding-bottom: 0;
}

</style>