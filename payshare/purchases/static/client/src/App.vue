<template>
  <v-app :dark="dark">
    <v-navigation-drawer
      v-if="collective"
      v-model="drawer"
      app
      fixed
      :dark="dark"
      :clipped="$vuetify.breakpoint.mdAndDown"
      :width="$vuetify.breakpoint.width <= 320 ? 280 : 300"
    >
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
            <v-list-tile-title class="auto-height">
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
          <v-list-tile
            v-if="showCreationButton"
            @click="(() => showCreateUpdateTransferDialog = true)"
          >
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
    <v-toolbar
      app
      fixed
      dark
      :color="!isLoginPage ? 'primary' : null"
      :class="{'light': isLoginPage,
               'auto-height': isLoginPage}"
      flat
    >
      <v-toolbar-side-icon
        v-if="!isLoginPage && $store.getters.isLoggedIn && !collective.logo_image_url"
        @click.stop="drawer = !drawer"
      />
      <v-btn
        v-if="$store.getters.isLoggedIn && collective.logo_image_url"
        @click.stop="drawer = !drawer"
        icon
      >
        <img
          :src="collective.logo_image_url"
          width="36"
          height="36"
        >
      </v-btn>
      <v-spacer v-if="isLoginPage"></v-spacer>
      <v-toolbar-title :class="{'black--text': isLoginPage,
                                'text--wrap': isLoginPage}">
        <span v-if="!$store.getters.isLoggedIn"
              class="subheading">
          {{ title }}
        </span>
        <span v-else>
          {{ collective.name }}
        </span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-layout
        v-if="collective && collective.readonly"
        align-center
        class="warning--text no-grow clickable"
        @click="displayReadOnlyAlert()"
      >
        <v-icon
          class="mr-1"
          color="warning"
        >
          lock
        </v-icon>
        <strong v-if="$vuetify.breakpoint.smAndUp">
          {{ $t('readOnly') }}
        </strong>
      </v-layout>
      <v-btn @click="reloadPage()"
             icon
             :title="$t('reloadPage')">
        <v-icon>refresh</v-icon>
      </v-btn>
      <v-btn
        v-if="!isLoginPage && $store.getters.isLoggedIn && $vuetify.breakpoint.smAndUp"
        icon
        :title="$t('logout')"
        @click="logout()"
      >
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
         v-if="showCreationButton"
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
        <v-icon
         :medium="$vuetify.breakpoint.smAndDown"
         :large="$vuetify.breakpoint.mdAndUp"
        >
          add
        </v-icon>
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
          <v-btn
            icon
            large
            :title="$t('logout')"
            @click="showSelectMemberDialog = false; logout()"
          >
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
    return {
      dark: false,
      title: 'Payshare',
      showSelectMemberDialog: false,
      showCreateUpdateTransferDialog: false,
    }
  },
  computed: {
    drawer: {
      get() {
        return this.$store.state.drawer
      },
      set(drawer) {
        this.$store.commit('SET_DRAWER', drawer)
      }
    },
    isLoginPage() {
      return this.$route.name === 'login'
    },
    collective() {
      return this.$store.state.collective
    },
    busy() {
      return this.$store.state.busy
    },
    showCreationButton() {
      return (
        !this.isLoginPage &&
        (this.collective && !this.collective.readonly)
      );
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
  mounted() {
    if (this.$store.getters.isLoggedIn) {
      this.refreshCollective()

      if (this.uuid) {
        this.$router.push(`/${this.uuid}/transfers`)
      }
    }

    this.rememberSelectedMember()

    this.setInitialDrawerState()
    this.checkIfWeNeedToChooseMember()

    this.$bus.$on('logged-in', this.checkIfWeNeedToChooseMember)
  },
  methods: {
    refreshCollective() {
      this.$store.dispatch('RETRIEVE_COLLECTIVE_USING_TOKEN')
    },
    displayReadOnlyAlert() {
      window.alert(this.$t('readOnlyAlert'))
    },
    setInitialDrawerState() {
      if (this.$vuetify.breakpoint.lgAndUp) {
        this.drawer = true
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
        this.$store.commit('RESET_ALL')
        this.$router.push('/unknown')
      }
    },
    reloadPage() {
      location.reload()
    },
  },
}
</script>

<style>

.navigation-drawer {
  padding-bottom: 0;
}

.auto-height {
  height: auto !important;
}

.list__tile__title--wrap {
  white-space: normal;
  height: auto;
}

.version-container {
  width: 100%;
  position: relative;
}

.version {
  width: 100%;
  text-align: end;
  position: absolute;
  font-size: 0.7rem;
  top: -17px;
}

.clickable {
  cursor: pointer;
}

.full-width {
  width: 100% !important;
}

.light {
  background: #FAFAFA !important;
}

.dbg,
.dbg *,
[dbg],
[dbg] * {
  outline: 1px solid red;
}

.text--wrap {
  white-space: normal;
}

.no-grow {
  flex-grow: 0 !important;
}

</style>
