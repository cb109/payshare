import Vue from 'vue'
import VueI18n from 'vue-i18n'

import messages from './translations';

Vue.use(VueI18n)

const defaultLocale = (navigator.language ||
                       navigator.userLanguage).slice(0, 2);
const i18n = new VueI18n({
  locale: defaultLocale,
  messages,
})

export default i18n
