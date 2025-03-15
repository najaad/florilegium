<template>
  <div id="app">
    <Navigation />
    <router-view />
  </div>
</template>

<script>
import Navigation from "./components/Navigation.vue";

export default {
  components: { Navigation },
};
</script>

<style>
body {
  font-family: 'Inter', sans-serif;
  background-color: var(--green-light);
  color: var(--purple-darkest);
  margin: 0;
}

h1 {
  font-family: 'Merriweather', serif;
  text-align: center;
}
</style>
