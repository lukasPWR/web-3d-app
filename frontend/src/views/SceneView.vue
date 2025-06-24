<template>
  <div class="scene-view">
    <div class="header-with-navigation">
      <h1>3D Scene Editor</h1>
      <button @click="$router.push('/')" class="back-button">Return to Main Menu</button>
    </div>
    
    <!-- NEW: Model Drawing Tools -->
    <div class="drawing-tools-container">
      <ModelDrawer @model-created="handleModelCreated" />
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
          <p>No models in scene. Select models from the list below or use the drawing tools above to create models.</p>
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
import ModelDrawer from '@/components/ModelDrawer.vue';

export default {
  name: 'SceneView',
  components: {
    SimpleModelViewer,
    ModelSelector,
    ModelDrawer
  },
  setup() {
    const selectedModels = ref([]);
    
    // NEW: Handle model creation from drawing tools
    const handleModelCreated = (newModel) => {
      // FIXED: Improved automatic positioning calculation
      const modelCount = selectedModels.value.length;
      const spacing = 4; // Increased spacing between models
      const gridSize = Math.ceil(Math.sqrt(modelCount + 1));
      
      const row = Math.floor(modelCount / gridSize);
      const col = modelCount % gridSize;
      const gridOffset = (gridSize - 1) * spacing / 2;
      
      // FIXED: Better initial scale for new models
      const initialScale = 1.5; // Slightly larger initial scale
      
      // Position the new model in the grid
      const modelWithPosition = {
        ...newModel,
        position: [
          col * spacing - gridOffset,
          0,
          row * spacing - gridOffset
        ],
        rotation: [0, 0, 0],
        scale: [initialScale, initialScale, initialScale] // FIXED: Apply better initial scale
      };
      
      selectedModels.value.push(modelWithPosition);
      
      console.log(`Added model ${newModel.id} at position:`, modelWithPosition.position, 'with scale:', initialScale);
    };
    
    const handleModelPositionChanged = (modelId, newPosition) => {
      const model = selectedModels.value.find(m => m.id === modelId);
      if (model) {
        model.position = newPosition;
      }
    };
    
    const handleModelRotationChanged = (modelId, newRotation) => {
      const model = selectedModels.value.find(m => m.id === modelId);
      if (model) {
        model.rotation = newRotation;
      }
    };
    
    const handleModelScaleChanged = (modelId, newScale) => {
      const model = selectedModels.value.find(m => m.id === modelId);
      if (model) {
        model.scale = newScale;
      }
    };
    
    const handleModelMaterialChanged = (modelId, newMaterial) => {
      const model = selectedModels.value.find(m => m.id === modelId);
      if (model) {
        model.material = newMaterial;
      }
    };
    
    return {
      selectedModels,
      handleModelCreated,
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
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100vh;
}

.header-with-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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

.drawing-tools-container {
  margin-bottom: 10px;
}

.scene-container {
  width: 100%;
  height: 75vh; /* Increased from 60vh to give more space to the scene */
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
  max-height: 20vh; /* Reduced from 35vh to make it more compact */
  overflow-y: auto; /* Make it scrollable */
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: white;
  margin-top: 10px;
}
</style>
