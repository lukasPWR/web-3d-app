<template>
  <div class="model-selector">
    <h2>Available Models</h2>
    
    <div v-if="loading" class="loading">Loading models...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else class="model-selection-grid">
      <div 
        v-for="model in availableModels" 
        :key="model.id" 
        class="model-card"
        :class="{ 'model-selected': isModelSelected(model.id) }"
        @click="toggleModel(model)"
      >
        <div class="model-card-header">
          <h3>{{ model.name }}</h3>
          <span class="model-format">{{ model.format }}</span>
        </div>
        
        <div class="model-card-body">
          <p class="model-description">{{ model.description }}</p>
        </div>
        
        <div class="model-card-footer">
          <button 
            class="select-button"
            :class="{ 'remove-button': isModelSelected(model.id) }"
          >
            {{ isModelSelected(model.id) ? 'Remove' : 'Add to Scene' }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="edit-mode-info">
      <p><strong>💡 Tip:</strong> Use "Edit Mode" in the 3D viewer to move objects by clicking and using arrow controls!</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'ModelSelector',
  emits: ['update:selected-models'],
  props: {
    selectedModels: {
      type: Array,
      default: () => []
    }
  },
  setup(props, { emit }) {
    const availableModels = ref([]);
    const loading = ref(true);
    const error = ref(null);
    
    // Fetch available models
    const fetchModels = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/models');
        availableModels.value = response.data;
      } catch (err) {
        console.error('Failed to fetch models:', err);
        error.value = 'Failed to load models. Please try again later.';
      } finally {
        loading.value = false;
      }
    };
    
    // Check if a model is selected
    const isModelSelected = (modelId) => {
      return props.selectedModels.some(model => model.id === modelId);
    };
    
    // Toggle model selection
    const toggleModel = (model) => {
      if (isModelSelected(model.id)) {
        removeModel(model.id);
      } else {
        addModel(model);
      }
    };
    
    // Add model to selection
    const addModel = (model) => {
      // Calculate automatic position based on existing models count
      const modelCount = props.selectedModels.length;
      const spacing = 3; // Distance between models
      const gridSize = Math.ceil(Math.sqrt(modelCount + 1)); // Grid dimensions
      
      // Calculate position in grid
      const row = Math.floor(modelCount / gridSize);
      const col = modelCount % gridSize;
      
      // Center the grid around origin
      const gridOffset = (gridSize - 1) * spacing / 2;
      
      const autoPosition = {
        x: (col * spacing) - gridOffset,
        y: 0,
        z: (row * spacing) - gridOffset
      };
      
      const modelWithDefaults = {
        ...model,
        // Ensure we have the correct property name for the model path
        modelPath: model.modelUrl || model.modelPath,
        position: autoPosition,
        scale: 1,
        rotation: { x: 0, y: 0, z: 0 },
        color: '#' + Math.floor(Math.random()*16777215).toString(16), // Random color
        material: {
          roughness: 0.7,
          metalness: 0.1,
          emissive: '#000000',
          emissiveIntensity: 0.0
        }
      };
      
      console.log('Adding model to selection:', modelWithDefaults); // Debug log
      
      const updatedSelection = [...props.selectedModels, modelWithDefaults];
      emit('update:selected-models', updatedSelection);
    };
    
    // Remove model from selection
    const removeModel = (modelId) => {
      const updatedSelection = props.selectedModels.filter(model => model.id !== modelId);
      emit('update:selected-models', updatedSelection);
    };
    
    onMounted(fetchModels);
    
    return {
      availableModels,
      loading,
      error,
      isModelSelected,
      toggleModel,
      removeModel,
      selectedModels: props.selectedModels
    };
  }
};
</script>

<style scoped>
.model-selector {
  margin-bottom: 0.5rem; /* Reduced from 1rem */
  height: 100%;
  display: flex;
  flex-direction: column;
}

h2 {
  margin-bottom: 0.3rem; /* Reduced from 0.5rem */
  font-size: 1.1rem; /* Smaller title */
  flex-shrink: 0;
  padding: 0.5rem; /* Add padding to header */
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  margin: 0; /* Remove margin */
}

.loading, .error {
  padding: 0.5rem;
  text-align: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.error {
  color: #f44336;
  background-color: #ffebee;
}

.model-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); /* Even smaller cards */
  gap: 0.3rem; /* Smaller gap */
  margin-bottom: 0;
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  border: none; /* Remove border since container has it */
  border-radius: 0;
  background-color: transparent;
  max-height: none;
}

.model-card {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.3rem; /* Even smaller padding */
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 95px; /* Smaller height */
  font-size: 0.75rem; /* Smaller font */
  background-color: white;
}

.model-card:hover {
  border-color: #2196f3;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.model-selected {
  border-color: #4CAF50;
  background-color: #f1f8e9;
}

.model-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.3rem;
}

.model-card h3 {
  margin: 0;
  font-size: 0.8rem; /* Smaller title */
  color: #333;
  line-height: 1.1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.model-format {
  font-size: 0.6rem; /* Smaller format tag */
  padding: 0.05rem 0.2rem;
  background-color: #e0e0e0;
  border-radius: 2px;
  color: #666;
}

.model-card-body {
  flex-grow: 1;
  margin-bottom: 0.5rem;
}

.model-description {
  color: #666;
  font-size: 10px; /* Smaller description */
  margin-top: 2px;
  display: -webkit-box;
  -webkit-line-clamp: 1; /* Only 1 line instead of 2 */
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.1;
}

.select-button {
  width: 100%;
  padding: 0.2rem; /* Smaller button padding */
  border: none;
  border-radius: 3px;
  background-color: #2196f3;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.65rem; /* Smaller button text */
}

.select-button:hover {
  background-color: #1976d2;
}

.remove-button {
  background-color: #f44336;
}

.remove-button:hover {
  background-color: #d32f2f;
}

.edit-mode-info {
  background-color: #e3f2fd;
  border: 1px solid #2196f3;
  border-radius: 6px;
  padding: 4px 8px; /* Smaller padding */
  margin: 0.5rem; /* Add margin around */
  flex-shrink: 0;
}

.edit-mode-info p {
  margin: 0;
  color: #1976d2;
  font-size: 11px; /* Smaller info text */
}
</style>
