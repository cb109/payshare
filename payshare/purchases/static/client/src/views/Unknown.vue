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
                <a :href="'/' + prevKey">
                  {{ prevKey }}
                </a>
            </li>
          </ul>
        </div>
    </v-layout>
  </v-container>
</template>


<script>

export default {
  name: 'unknown',
  computed: {
    previousCollectiveKeys() {
      return this.$store.state.previousCollectiveKeys || []
    },
  },
  created() {
    this.$store.commit('LOAD_PREVIOUS_COLLECTIVE_KEYS_FROM_LOCALSTORAGE')
  },
}

</script>