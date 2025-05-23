<script setup>
import { defineProps, defineEmits } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'

const props = defineProps({
  models: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['model-deleted'])

const deleteModel = async (modelId) => {
  if (!confirm('Are you sure you want to delete this model?')) {
    return
  }
  
  try {
    await axios.delete(`/api/models/${modelId}`)
    emit('model-deleted')
  } catch (err) {
    console.error('Error deleting model:', err)
    alert('Failed to delete model. Please try again.')
  }
}
</script>

<template>
  <div class="model-list">
    <h2>Available 3D Models</h2>
    <ul>
      <li v-for="model in models" :key="model.id" class="model-item">
        <div class="model-info">
          <RouterLink :to="{ name: 'model', params: { id: model.id } }" class="model-link">
            {{ model.name }}
          </RouterLink>
          <span class="model-format">{{ model.format }}</span>
        </div>
        <div class="model-actions">
          <button @click="deleteModel(model.id)" class="delete-button" title="Delete model">
            🗑️
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.model-list {
  margin-top: 2rem;
}

h2 {
  margin-bottom: 1rem;
}

ul {
  list-style-type: none;
  padding: 0;
}

.model-item {
  margin: 0.5rem 0;
  padding: 0.75rem;
  background-color: #f5f5f5;
  border-radius: 4px;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-item:hover {
  background-color: #e0e0e0;
  transform: translateX(5px);
}

.model-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.model-link {
  font-weight: bold;
  color: #2c3e50;
}

.model-format {
  font-size: 0.8rem;
  color: #666;
  background-color: #e0e0e0;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
}

.delete-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.delete-button:hover {
  background-color: rgba(244, 67, 54, 0.1);
}
</style>
