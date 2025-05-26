<template>
  <div class="model-view">
    <div v-if="loading" class="loading">Loading model data...</div>
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="$router.push('/')">Return to Home</button>
    </div>
    <div v-else class="model-container">
      <h1>{{ model.name }}</h1>
      <p>{{ model.description }}</p>
      
      <div class="model-viewer-wrapper">
        <SimpleModelViewer 
          :models="[{
            id: model.id,
            modelPath: model.modelUrl,
            color: model.color || '#cccccc'
          }]"
        />
      </div>
      
      <div class="actions">
        <button @click="$router.push('/')">Back to Models</button>
        <button @click="deleteModel" class="delete-btn">Delete Model</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import SimpleModelViewer from '@/components/SimpleModelViewer.vue';
import { useRoute } from 'vue-router';

export default {
  name: 'ModelView',
  components: {
    SimpleModelViewer
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  setup(props, { emit }) {
    const model = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const route = useRoute();

    const fetchModel = async (modelId) => {
      // Check if modelId is valid
      if (!modelId) {
        error.value = 'Invalid model ID';
        loading.value = false;
        return;
      }

      try {
        loading.value = true;
        error.value = null;
        const response = await axios.get(`/api/models/${modelId}`);
        model.value = response.data;
      } catch (err) {
        console.error(err);
        error.value = `Failed to load model: ${err.message}`;
      } finally {
        loading.value = false;
      }
    };

    const deleteModel = async () => {
      if (!confirm('Are you sure you want to delete this model?')) {
        return;
      }

      try {
        loading.value = true;
        await axios.delete(`/api/models/${props.id}`);
        emit('model-deleted');
        // Navigate back to home page
        window.location.href = '/';
      } catch (err) {
        console.error(err);
        error.value = `Failed to delete model: ${err.message}`;
        loading.value = false;
      }
    };

    // Watch for changes to the ID prop
    watch(() => props.id, (newId) => {
      if (newId) {
        fetchModel(newId);
      }
    });

    onMounted(() => {
      fetchModel(props.id);
    });

    return {
      model,
      loading,
      error,
      deleteModel
    };
  }
};
</script>

<style scoped>
.model-view {
  padding: 20px;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading, .error {
  text-align: center;
  padding: 50px;
}

.error {
  color: #d32f2f;
}

.model-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.model-viewer-wrapper {
  width: 100%;
  min-height: 700px;
}

/* Override the deep selector syntax for Vue 3 */
:deep(.model-viewer-container) {
  width: 100% !important;
  height: 80vh !important;
  min-height: 700px !important;
}

.model-container h1, 
.model-container p {
  text-align: center;
  width: 100%;
  margin-bottom: 20px;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

button {
  padding: 8px 16px;
  background-color: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #0b7dda;
}

.delete-btn {
  background-color: #f44336;
}

.delete-btn:hover {
  background-color: #d32f2f;
}
</style>
