<script setup>
import { ref, onMounted } from 'vue'
import ModelList from '../components/ModelList.vue'
import ModelUploader from '../components/ModelUploader.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const models = ref([])
const loading = ref(true)
const error = ref(null)
const showUploader = ref(false)

const fetchModels = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/models')
    models.value = response.data
  } catch (err) {
    error.value = 'Failed to load models. Please try again later.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleModelUploaded = (newModel) => {
  models.value.push(newModel)
  showUploader.value = false
}

const goToSceneEditor = () => {
  router.push('/scene')
}

onMounted(fetchModels)
</script>

<template>
  <main>
    <div class="header-area">
      <h1>Web 3D Application</h1>
      <div class="header-actions">
        <button @click="showUploader = !showUploader" class="upload-button">
          {{ showUploader ? 'Cancel Upload' : 'Upload New Model' }}
        </button>
        <button @click="goToSceneEditor" class="scene-button">
          Create 3D Scene
        </button>
      </div>
    </div>
    
    <p>Welcome to the 3D model viewer application. Upload models or create multi-model scenes!</p>
    
    <ModelUploader 
      v-if="showUploader" 
      @upload-success="handleModelUploaded" 
      @upload-cancel="showUploader = false" 
    />
    
    <div v-if="loading" class="status-message">Loading models...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>
    <div v-else-if="models.length === 0" class="status-message">No models available. Upload one to get started!</div>
    <ModelList v-else :models="models" @model-deleted="fetchModels" />
  </main>
</template>

<style scoped>
main {
  padding: 1rem;
}

h1 {
  margin-bottom: 1rem;
}

.header-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.upload-button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.upload-button:hover {
  background-color: #45a049;
}

.scene-button {
  padding: 0.5rem 1rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.scene-button:hover {
  background-color: #0b7dda;
}

.status-message {
  padding: 1rem;
  margin-top: 1rem;
  background-color: #f8f8f8;
  border-radius: 4px;
  text-align: center;
}

.error {
  color: red;
  background-color: #ffebee;
}
</style>
