<script setup>
import { defineProps } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  models: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <div class="model-list">
    <h2>Available 3D Models</h2>
    <ul>
      <li v-for="model in models" :key="model.id">
        <RouterLink :to="{ name: 'model', params: { id: model.id } }">
          {{ model.name }}
        </RouterLink>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.model-list {
  margin-top: 2rem;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  margin: 0.5rem 0;
  padding: 0.5rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  transition: all 0.3s;
}

li:hover {
  background-color: #e0e0e0;
  transform: translateX(5px);
}
</style>
