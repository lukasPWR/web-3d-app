<template>
  <div class="scene-view">
    <h1>3D Scene Editor</h1>
    
    <div class="scene-container">
      <SimpleModelViewer 
        :models="selectedModels"
        v-if="selectedModels.length > 0"
      />
      <div v-else class="empty-scene">
        <p>No models in scene. Select models from the list below to add.</p>
      </div>
    </div>
    
    <div class="model-selector-container">
      <ModelSelector
        :selectedModels="selectedModels"
        @update:selected-models="selectedModels = $event"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import SimpleModelViewer from '@/components/SimpleModelViewer.vue';
import ModelSelector from '@/components/ModelSelector.vue';

export default {
  name: 'SceneView',
  components: {
    SimpleModelViewer,
    ModelSelector
  },
  setup() {
    const selectedModels = ref([]);
    
    return {
      selectedModels
    };
  }
};
</script>

<style scoped>
.scene-view {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

h1 {
  margin-bottom: 20px;
}

.scene-container {
  width: 100%;
  height: 500px; /* Fixed height for the 3D viewer */
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.empty-scene {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  color: #666;
}

.model-selector-container {
  width: 100%;
}
</style>
