/* eslint-disable no-console */

// FIXME: service worker is currently broken, there are problems running
//  it: Error during service worker registration: Error: Service worker
// not found at /static/service-worker.js
//
// Even if it would work, we are currently serving it from /static/ so
// it won't be able to control /, which is what we'd want. We need to
// find wa way to serve it from root, maye with a Django view serving
// just that static file.

import { register } from 'register-service-worker'

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready () {
      console.log(
        'App is being served from cache by a service worker.\n' +
        'For more details, visit https://goo.gl/AFskqB'
      )
    },
    cached () {
      console.log('Content has been cached for offline use.')
    },
    updated () {
      console.log('New content is available; please refresh.')
    },
    offline () {
      console.log('No internet connection found. App is running in offline mode.')
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })
}
