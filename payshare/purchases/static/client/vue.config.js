const express = require('express')

module.exports = {
  lintOnSave: false,

  // The baseUrl will be the prefix for all generated files e.g.
  // app.js, vendor.cs / it allows us to integrate the webpack assets
  // with Django's development server and to serve it with Django in
  // production (after running collectstatic).
  // See: https://github.com/vuejs/vue-cli/issues/976
  baseUrl: 'static',

  // Requests for files at /static/ will be found in the 'public' folder
  // during dev, before Django will later serve them from the actual URL
  // in production. See: https://github.com/vuejs/vue-cli/issues/1102
  devServer: {
    proxy: null,
    before: app => {
      app.use('/static', express.static('public'));
    },
  },
}