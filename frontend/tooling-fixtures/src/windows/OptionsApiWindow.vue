<!-- Negative lint fixture (US-01.06 AC2): the Options API must fail vue/component-api-style. -->
<script lang="ts">
export default {
  name: 'OptionsApiWindow',
  data() {
    return { title: 'Options API' }
  },
}
</script>

<template>
  <h2>{{ title }}</h2>
</template>
