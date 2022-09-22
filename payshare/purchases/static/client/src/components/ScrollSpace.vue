<template>

<div :style="{'min-height': heightPixels}"></div>

</template>

<script>

export default {
  name: 'scroll-space',
  props: {
    'height': {
      type: Number,
      required: true,
    },
  },
  computed: {
    heightPixels() {
      return this.height + 'px'
    },
  },
}

</script>
