<template>
  <div class="create-model-view">
    <div class="header-with-navigation">
      <h1>Create 3D Model</h1>
      <button @click="$router.push('/')" class="back-button">Return to Main Menu</button>
    </div>
    
    <div class="create-content">
      <div class="info-section">
        <h2>Programmatic Model Creation</h2>
        <p>Use the powerful drawing tools below to create 3D models programmatically using Blender's Python API.</p>
        
        <div class="features-grid">
          <div class="feature-card">
            <h3>🎯 Quick Primitives</h3>
            <p>Create basic shapes like cubes, spheres, cylinders instantly</p>
          </div>
          <div class="feature-card">
            <h3>📏 Line Drawing</h3>
            <p>Draw custom polylines from point sequences</p>
          </div>
          <div class="feature-card">
            <h3>⚙️ Advanced Sessions</h3>
            <p>Combine multiple drawing commands in one session</p>
          </div>
          <div class="feature-card">
            <h3>🎨 Material Control</h3>
            <p>Set colors and material properties for your models</p>
          </div>
        </div>
      </div>
      
      <div class="drawing-section">
        <ModelDrawer @model-created="handleModelCreated" />
      </div>
      
      <div v-if="createdModels.length > 0" class="created-models-section">
        <h3>Recently Created Models</h3>
        <div class="created-models-grid">
          <div v-for="model in createdModels" :key="model.id" class="created-model-card">
            <h4>{{ model.name }}</h4>
            <p>{{ model.description }}</p>
            <div class="model-actions">
              <button @click="viewModel(model)" class="view-btn">View</button>
              <button @click="addToScene(model)" class="scene-btn">Add to Scene</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ModelDrawer from '@/components/ModelDrawer.vue';

export default {
  name: 'CreateModelView',
  components: {
    ModelDrawer
  },
  setup() {
    const router = useRouter();
    const createdModels = ref([]);
    
    const handleModelCreated = (newModel) => {
      createdModels.value.unshift(newModel);
      
      // Show success notification
      alert(`Model "${newModel.name}" created successfully!`);
    };
    
    const viewModel = (model) => {
      router.push(`/model/${model.id}`);
    };
    
    const addToScene = (model) => {
      // Navigate to scene editor with this model
      router.push('/scene');
    };
    
    return {
      createdModels,
      handleModelCreated,
      viewModel,
      addToScene
    };
  }
};
</script>

<style scoped>
.create-model-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-with-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
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

.create-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.info-section {
  background-color: #f8f9fa;
  padding: 30px;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.info-section h2 {
  margin: 0 0 15px 0;
  color: #333;
}

.info-section p {
  color: #666;
  font-size: 16px;
  margin-bottom: 25px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.feature-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.feature-card h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.feature-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.drawing-section {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.created-models-section {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 10px;
  border: 1px solid #e9ecef;
}

.created-models-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.created-models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.created-model-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.created-model-card h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.created-model-card p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.model-actions {
  display: flex;
  gap: 10px;
}

.view-btn, .scene-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.view-btn {
  background-color: #007bff;
  color: white;
}

.view-btn:hover {
  background-color: #0056b3;
}

.scene-btn {
  background-color: #28a745;
  color: white;
}

.scene-btn:hover {
  background-color: #218838;
}
</style>
