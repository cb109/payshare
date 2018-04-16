<template>
  <v-app dark>
    <v-navigation-drawer app
                         fixed
                         clipped
                         v-model="drawer">
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
    </v-navigation-drawer>
    <v-toolbar app
               fixed
               clipped-left>
      <v-toolbar-side-icon
        @click.stop="drawer = !drawer">
      </v-toolbar-side-icon>
      <v-toolbar-title>
        {{ title }}
        </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-toolbar>
    <v-content>
      {{ uuid }}
      <router-view/>
    </v-content>
  </v-app>
</template>

<script>

export default {
  name: 'App',
  data () {
    return {
      drawer: true,
      title: 'Payshare',
      menuItems: [
        {
          icon: 'add',
          title: 'Add Purchase',
        },
      ]
    }
  },
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
    fetchCollective(key) {
      // yarn add axios etc.
    },
  }
}
</script>
