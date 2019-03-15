<template>
  <v-app :dark="dark">
    <v-navigation-drawer app
                         :dark="dark"
                         fixed
                         :clipped="$vuetify.breakpoint.mdAndDown"
                         v-model="drawer"
                         :width="$vuetify.breakpoint.width <= 320 ? 280 : 300"
                         v-if="$store.getters.isLoggedIn">
      <v-layout column
                fill-height>
        <v-list>
          <!-- Selected User -->
          <selected-member-list-tile
            :label="$t('whoAreYou')">
          </selected-member-list-tile>
          <!-- Balance for selected User -->
          <v-list-tile>
            <v-list-tile-action></v-list-tile-action>
            <v-list-tile-title>
              <span class="headline"
                    :class="{'red--text': selectedMemberBalance < 0,
                             'default--text': selectedMemberBalance == 0,
                             'green--text': selectedMemberBalance > 0}">
                {{ selectedMemberBalance }}
                {{ collective.currency_symbol }}
              </span>
            </v-list-tile-title>
          </v-list-tile>
          <v-divider></v-divider>
          <!-- Add new Entry -->
          <v-list-tile @click="(() => showCreateUpdateTransferDialog = true)">
            <v-list-tile-action>
              <v-icon>add</v-icon>
            </v-list-tile-action>
            <v-list-tile-title>
              {{ $t('addEntry') }}
              </v-list-tile-title>
          </v-list-tile>
        </v-list>
        <v-spacer></v-spacer>
        <v-list>
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
               :class="{'light': isLoginPage,
                        'auto-height': isLoginPage}"
               flat>
      <v-toolbar-side-icon
        v-if="$store.getters.isLoggedIn"
        @click.stop="drawer = !drawer">
      </v-toolbar-side-icon>
      <v-spacer v-if="isLoginPage"></v-spacer>
      <v-toolbar-title :class="{'black--text': isLoginPage,
                                'text--wrap': isLoginPage}">
        <span v-if="!$store.getters.isLoggedIn"
              class="subheading">
          {{ title }}<span v-if="uuid">: {{ uuid }}</span>
        </span>
        <span v-else>
          {{ collective.name }}
        </span>
        </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="reloadPage()"
             icon
             :title="$t('reloadPage')">
        <v-icon>refresh</v-icon>
      </v-btn>
      <v-btn v-if="$store.getters.isLoggedIn && $vuetify.breakpoint.smAndUp"
             @click="logout()"
             icon
             :title="$t('logout')">
        <v-icon>exit_to_app</v-icon>
      </v-btn>
    </v-toolbar>
    <v-progress-linear
      v-if="busy"
      color="accent"
      style="position: fixed;
             margin: 0.5rem 0"
      :style="{'top': $vuetify.breakpoint.xsOnly ? '48px' : '56px'}"
      indeterminate
    ></v-progress-linear>
    <v-content>
      <v-btn
         v-if="!isLoginPage"
         fab
         fixed
         right
         bottom
         color="primary"
         dark
         :large="$vuetify.breakpoint.mdAndUp"
         :title="$t('addEntry')"
         @click="(() => showCreateUpdateTransferDialog = true)"
      >
        <v-icon>add</v-icon>
      </v-btn>
      <v-slide-y-transition mode="out-in">
        <router-view :key="$route.fullPath" />
      </v-slide-y-transition>
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
    <create-update-transfer-dialog
      :show.sync="showCreateUpdateTransferDialog"
    ></create-update-transfer-dialog>
  </v-app>
</template>

<script>

import collectiveStats from '@/mixins/collectiveStats'
import selectedMember from '@/mixins/selectedMember'
import uuid from '@/mixins/uuid'

import CreateUpdateTransferDialog from '@/components/CreateUpdateTransferDialog'
import SelectedMemberListTile from '@/components/SelectedMemberListTile'

export default {
  name: 'App',
  mixins: [
    collectiveStats,
    selectedMember,
    uuid,
  ],
  components: {
    CreateUpdateTransferDialog,
    SelectedMemberListTile,
  },
  data () {
    const vm = this
    return {
      drawer: false,
      dark: false,
      title: 'Payshare',
      showSelectMemberDialog: false,
      showCreateUpdateTransferDialog: false,
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
      if (this.collective) {
        // It may be outdated, get a fresh dataset from the API.
        this.$store.dispatch('RETRIEVE_COLLECTIVE_USING_TOKEN')
      }
    },
    checkIfWeNeedToChooseMember() {
      if (this.$store.getters.isLoggedIn && !this.selectedMember) {
        this.showSelectMemberDialog = true
      }
    },
    logout() {
      const confirmed = confirm(this.$t('confirmLogout'))
      if (confirmed) {
        const key = this.collective.key
        this.$store.commit('RESET_ALL')
        this.$router.push('/' + key)
      }
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

.clickable {
  cursor: pointer;
}

.full-width {
  width: 100% !important;
}

.light {
  background: #FAFAFA !important;
}

.dbg {
  border: 1px solid red;
}

.dbg * {
  border: 1px solid red;
}

.auto-height .toolbar__content {
  padding-top: 8px;
  height: auto !important;
}

.text--wrap {
  white-space: normal;
}

.list__tile__title--wrap {
  white-space: normal;
  height: auto;
}

</style>
