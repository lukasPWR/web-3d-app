<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'
import ModelViewer from '../components/ModelViewer.vue'

const route = useRoute()
const modelId = computed(() => parseInt(route.params.id))

// This would typically come from an API call
const model = computed(() => {
  const models = [
    { id: 1, name: "Model 1", path: "/models/model1.glb" },
    { id: 2, name: "Model 2", path: "/models/model2.glb" }
  ]
  return models.find(m => m.id === modelId.value) || { id: 0, name: "Unknown Model", path: "" }
})
</script>

<template>
  <div class="model-view">
    <h1>{{ model.name }}</h1>
    
    <div class="model-container">
      <TresCanvas v-if="model.path" window-size>
        <TresAmbientLight :intensity="1" />
        <TresDirectionalLight :position="[10, 10, 10]" :intensity="1.5" :cast-shadow="true" />
        
        <ModelViewer :model-path="model.path" />
        
        <OrbitControls />
      </TresCanvas>
      <div v-else class="error">Model not found</div>
    </div>
  </div>
</template>

<style scoped>
.model-view {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.model-container {
  flex: 1;
  min-height: 500px;
  background-color: #f8f8f8;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: red;
}
</style>
