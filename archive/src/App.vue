<template>
  <div id="app">
    <SidebarNavigation />
    <router-view />
  </div>
</template>

<script>
import SidebarNavigation from "./components/SidebarNavigation.vue";

export default {
  components: { SidebarNavigation },
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
