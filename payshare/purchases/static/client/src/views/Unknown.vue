<template>
  <v-container fluid
               fill-height>
    <v-layout align-center
              column
              class="mt-4">
      <h1 class="headline">
        {{ $t('unknownHint') }}
      </h1>
      <div v-if="previousCollectiveKeys.length"
           class="mt-4">
        <h4 class="subheading mb-2">
          {{ $t('beenHereBefore') }}:
        </h4>
        <ul>
          <li v-for="prevKey in previousCollectiveKeys"
              :key="prevKey">
              <router-link :to="'/' + prevKey">
                <span v-if="collectiveNameByKey[prevKey]">
                  {{ collectiveNameByKey[prevKey] }}
                </span>
                <span v-else>
                  {{ prevKey }}
                </span>
              </router-link>
          </li>
        </ul>
      </div>
      <v-layout
        align-center
        class="grey--text text--lighten-1"
      >
        <div>
          v{{ version }}
        </div>
      </v-layout>
    </v-layout>
  </v-container>
</template>


<script>

export default {
  computed: {
    previousCollectiveKeys() {
      return this.$store.state.previousCollectiveKeys || []
    },
    collectiveNameByKey() {
      return this.$store.state.collectiveNameByKey
    },
    version() {
      return this.$store.state.version
    },
  },
  created() {
    this.$store.commit('LOAD_PREVIOUS_COLLECTIVE_KEYS_FROM_LOCALSTORAGE')
    this.$store.commit('LOAD_COLLECTIVE_NAME_BY_KEY_MAP_FROM_LOCALSTORAGE')

    this.fetchVersionIfNeeded()
  },
  methods: {
    fetchVersionIfNeeded() {
      if (this.version) {
        return
      }
      this.$store.dispatch('RETRIEVE_VERSION')
    },
  },
}

</script>