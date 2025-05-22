<script setup>
import { ref, onMounted } from 'vue'
import ModelList from '../components/ModelList.vue'
import axios from 'axios'

const models = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    const response = await axios.get('/api/models')
    models.value = response.data
  } catch (err) {
    error.value = 'Failed to load models. Please try again later.'
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main>
    <h1>Web 3D Application</h1>
    <p>Welcome to the 3D model viewer application</p>
    
    <div v-if="loading">Loading models...</div>
    <div v-else-if="error">{{ error }}</div>
    <ModelList v-else :models="models" />
  </main>
</template>

<style scoped>
main {
  padding: 1rem;
}

h1 {
  margin-bottom: 1rem;
}
</style>
