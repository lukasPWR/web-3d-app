<template>
  <div class="scene-view">
    <div class="header-with-navigation">
      <h1>3D Scene Editor</h1>
      <button @click="$router.push('/')" class="back-button">Return to Main Menu</button>
    </div>
    
    <div class="scene-container">
      <div class="viewer-and-controls">
        <SimpleModelViewer 
          :models="selectedModels"
          @model-position-changed="handleModelPositionChanged"
          @model-rotation-changed="handleModelRotationChanged"
          @model-scale-changed="handleModelScaleChanged"
          @model-material-changed="handleModelMaterialChanged"
          v-if="selectedModels.length > 0"
        />
        <div v-else class="empty-scene">
          <p>No models in scene. Select models from the list below to add.</p>
        </div>
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
    
    // Handle position changes from edit mode
    const handleModelPositionChanged = ({ modelId, position }) => {
      const modelIndex = selectedModels.value.findIndex(model => model.id === modelId);
      if (modelIndex !== -1) {
        // Use Vue's reactivity properly to avoid unnecessary re-renders
        selectedModels.value[modelIndex] = {
          ...selectedModels.value[modelIndex],
          position: { ...position }
        };
      }
    };
    
    // Handle rotation changes from edit mode
    const handleModelRotationChanged = ({ modelId, rotation }) => {
      const modelIndex = selectedModels.value.findIndex(model => model.id === modelId);
      if (modelIndex !== -1) {
        selectedModels.value[modelIndex] = {
          ...selectedModels.value[modelIndex],
          rotation: { ...rotation }
        };
      }
    };
    
    // Handle scale changes from edit mode
    const handleModelScaleChanged = ({ modelId, scale }) => {
      const modelIndex = selectedModels.value.findIndex(model => model.id === modelId);
      if (modelIndex !== -1) {
        selectedModels.value[modelIndex] = {
          ...selectedModels.value[modelIndex],
          scale
        };
      }
    };
    
    // Handle material changes from edit mode
    const handleModelMaterialChanged = ({ modelId, material }) => {
      const modelIndex = selectedModels.value.findIndex(model => model.id === modelId);
      if (modelIndex !== -1) {
        const updatedModel = { ...selectedModels.value[modelIndex] };
        
        // Update the material object
        updatedModel.material = {
          ...updatedModel.material,
          ...material
        };
        
        // Also update the color property for consistency with ModelSelector
        if (material.color) {
          updatedModel.color = material.color;
        }
        
        selectedModels.value[modelIndex] = updatedModel;
      }
    };
    
    return {
      selectedModels,
      handleModelPositionChanged,
      handleModelRotationChanged,
      handleModelScaleChanged,
      handleModelMaterialChanged
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
  height: 100vh;
}

.header-with-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  padding: 8px 16px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #0b7dda;
}

h1 {
  margin: 0; /* Reset margin since it's now controlled by the parent div */
}

.scene-container {
  width: 100%;
  height: 75vh;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
}

.viewer-and-controls {
  width: 100%;
  height: 100%;
  display: flex;
}

.empty-scene {
  width: 100%;
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
