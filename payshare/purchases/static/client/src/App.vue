<template>
  <v-app :dark="dark">
    <v-navigation-drawer app
                         :dark="dark"
                         fixed
                         v-model="drawer"
                         :width="$vuetify.breakpoint.width <= 320 ? 260 : 300"
                         v-if="$store.getters.isLoggedIn">
      <v-layout column
                fill-height>
        <v-list>
          <!-- Selected User -->
          <selected-member-list-tile
            :label="$t('whoAreYou')">
          </selected-member-list-tile>
          <!-- Financial Status -->
          <v-list-tile>
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-content>
              <strong class="red--text headline">
                -&nbsp;132.56 $
              </strong>
            </v-list-tile-content>
          </v-list-tile>
          <!-- Actionable menu items -->
          <v-divider></v-divider>
          <v-list-tile v-for="(item, i) in menuItems"
                       :key="i"
                       @click="item.action ? item.action() : null">
            <v-list-tile-action>
              <v-icon>
                {{ item.icon }}
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                {{ $t(item.title) }}
                </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
        <v-spacer></v-spacer>
        <v-list>
          <v-divider></v-divider>
          <!-- Language -->
          <v-list-tile>
            <v-list-tile-action>
              <v-icon>
                language
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-select
                :label="$t('language')"
                v-model="$i18n.locale"
                :items="languages"
                item-value="locale"
                item-text="name">
              </v-select>
            </v-list-tile-content>
          </v-list-tile>
          <v-divider></v-divider>
          <!-- Logout -->
          <v-list-tile @click="logout()">
            <v-list-tile-action>
              <v-icon>
                exit_to_app
              </v-icon>
            </v-list-tile-action>
            <v-list-tile-content>
              <v-list-tile-title>
                {{ $t('logout') }}
              </v-list-tile-title>
            </v-list-tile-content>
          </v-list-tile>
        </v-list>
      </v-layout>
    </v-navigation-drawer>
    <v-toolbar app
               fixed
               dark
               :color="!isLoginPage ? 'primary' : null"
               :class="{'light': isLoginPage}"
               :flat="isLoginPage">
      <v-toolbar-side-icon
        v-if="$store.getters.isLoggedIn"
        @click.stop="drawer = !drawer">
      </v-toolbar-side-icon>
      <v-spacer v-if="isLoginPage"></v-spacer>
      <v-toolbar-title :class="{'black--text': isLoginPage}">
        <span v-if="!$store.getters.isLoggedIn">
          {{ title }}<span v-if="uuid">: {{ uuid }}</span>
        </span>
        <span v-else>
          {{ collective.name }}
        </span>
        </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-progress-circular v-if="busy"
                           size="20"
                           indeterminate></v-progress-circular>
      <v-btn @click="reloadPage()"
             icon>
        <v-icon>refresh</v-icon>
      </v-btn>
      <v-btn v-if="$store.getters.isLoggedIn"
             @click="logout()"
             icon>
        <v-icon>exit_to_app</v-icon>
      </v-btn>
    </v-toolbar>
    <v-content>
      <v-container>
        <v-slide-y-transition mode="out-in">
          <router-view :key="$route.fullPath" />
        </v-slide-y-transition>
      </v-container>
    </v-content>
    <!-- Show Select Member Dialog-->
    <v-dialog persistent
              max-width="480px"
              v-model="showSelectMemberDialog">
      <v-card>
        <v-toolbar flat
                   color="primary"
                   dark>
          <v-toolbar-title>
            <h3 class="headline">{{ $t('chooseMember') }}</h3>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon
                 large
                 @click="showSelectMemberDialog = false; logout()"
                 :title="$t('logout')">
            <v-icon>
              exit_to_app
            </v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text>
          <selected-member-list-tile
            :label="$t('whoAreYou')"
            @selected="(() => showSelectMemberDialog = false)">
          </selected-member-list-tile>
        </v-card-text>
      </v-card>
    </v-dialog>
    <!-- Create Purchase Dialog-->
    <create-purchase-dialog
      :show.sync="showCreatePurchaseDialog"
    ></create-purchase-dialog>
  </v-app>
</template>

<script>

import selectedMember from '@/mixins/selectedMember'
import uuid from '@/mixins/uuid'

import CreatePurchaseDialog from '@/components/CreatePurchaseDialog'
import SelectedMemberListTile from '@/components/SelectedMemberListTile'

export default {
  name: 'App',
  mixins: [
    selectedMember,
    uuid,
  ],
  components: {
    CreatePurchaseDialog,
    SelectedMemberListTile,
  },
  data () {
    const vm = this
    return {
      drawer: false,
      dark: false,
      title: 'Payshare',
      menuItems: [
        {
          icon: 'add',
          title: 'addPurchase',
          action() {
            vm.showCreatePurchaseDialog = true
          },
        },
      ],
      showSelectMemberDialog: false,
      showCreatePurchaseDialog: false,
    }
  },
  computed: {
    isLoginPage() {
      return this.$route.name === 'login'
    },
    collective() {
      return this.$store.state.collective
    },
    busy() {
      return this.$store.state.busy
    },
    languages() {
      const locales = Object.keys(this.$i18n.messages)
      locales.sort()
      const languages = locales.map(locale => {
        return {
          locale: locale,
          name: this.$t(locale),
        }
      })
      return languages
    },
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
    },
    checkIfWeNeedToChooseMember() {
      if (this.$store.getters.isLoggedIn && !this.selectedMember) {
        this.showSelectMemberDialog = true
      }
    },
    logout() {
      const key = this.collective.key
      this.$store.commit('RESET_ALL')
      this.$router.push('/' + key)
    },
    reloadPage() {
      location.reload()
    },
  },
  // FIXME: Dehydration of state races with created() and mounted() in
  //   other components and should better be handled explcitly, maybe
  //   using something like vuex-localstorage.
  created() {
    this.checkUrl()

    this.rememberCollective()
    this.rememberSelectedMember()

    if (this.$store.getters.isLoggedIn) {
      this.$router.push('/transfers')
    }
  },
  mounted() {
    this.setInitialDrawerState()
    this.checkIfWeNeedToChooseMember()

    this.$bus.$on('logged-in', this.checkIfWeNeedToChooseMember)
  },
}
</script>

<style>

.navigation-drawer {
  padding-bottom: 0;
}

</style>

<style>

.light {
  background: #FAFAFA !important;
}

.dbg {
  border: 1px solid red;
}

.dbg * {
  border: 1px solid red;
}

</style>