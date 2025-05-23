<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Home</RouterLink> |
        <RouterLink to="/scene">3D Scene Editor</RouterLink>
      </nav>
    </div>
  </header>

  <div class="content-container">
    <RouterView />
  </div>
</template>

<style>
/* Global styles to ensure proper sizing of the 3D viewer */
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.content-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  box-sizing: border-box;
}
</style>

<style scoped>
header {
  line-height: 1.5;
}

nav {
  width: 100%;
  font-size: 18px;
  text-align: center;
  margin-top: 2rem;
  margin-bottom: 2rem;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}
</style>
