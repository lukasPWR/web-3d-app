<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

<template>
  <div class="app-container">
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



.app-container {
  
  width: 100%;
  height: 100%;
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
  position: relative; /* Ensure proper stacking context */
  z-index: 1; /* Lower than header */
}
</style>

<style scoped>
header {
  line-height: 1.5;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative; /* Ensure header stays above content */
  z-index: 10; /* Higher z-index to keep header visible */
}

nav {
  width: 100%;
  font-size: 18px;
  text-align: center;
  margin-top: 1rem;
  margin-bottom: 1rem;
  padding: 0.5rem 0;
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
