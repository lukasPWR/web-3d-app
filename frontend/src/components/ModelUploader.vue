<script setup>
import { ref, defineEmits } from 'vue';
import axios from 'axios';

const emit = defineEmits(['upload-success', 'upload-cancel']);

const modelName = ref('');
const modelDescription = ref('');
const selectedFile = ref(null);
const isUploading = ref(false);
const uploadProgress = ref(0);
const error = ref(null);

const allowedExtensions = ['.obj', '.gltf', '.glb', '.fbx'];

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      error.value = `Unsupported file format. Supported formats: ${allowedExtensions.join(', ')}`;
      selectedFile.value = null;
      event.target.value = '';  // Reset the input
      return;
    }
    
    selectedFile.value = file;
    error.value = null;
    
    // Auto-fill name from filename if empty
    if (!modelName.value) {
      modelName.value = file.name.split('.')[0];
    }
  }
};

const uploadModel = async () => {
  if (!selectedFile.value) {
    error.value = 'Please select a file to upload';
    return;
  }
  
  if (!modelName.value.trim()) {
    error.value = 'Please enter a name for the model';
    return;
  }
  
  error.value = null;
  isUploading.value = true;
  uploadProgress.value = 0;
  
  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value);
    formData.append('name', modelName.value);
    formData.append('description', modelDescription.value);
    
    const response = await axios.post('/api/models/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        uploadProgress.value = percentCompleted;
      }
    });
    
    emit('upload-success', response.data);
    resetForm();
  } catch (err) {
    console.error('Upload error:', err);
    error.value = err.response?.data?.error || 'Upload failed. Please try again.';
  } finally {
    isUploading.value = false;
  }
};

const resetForm = () => {
  modelName.value = '';
  modelDescription.value = '';
  selectedFile.value = null;
  error.value = null;
  uploadProgress.value = 0;
  // Also reset the file input element
  const fileInput = document.getElementById('model-file-input');
  if (fileInput) fileInput.value = '';
};

const cancelUpload = () => {
  resetForm();
  emit('upload-cancel');
};
</script>

<template>
  <div class="model-uploader">
    <h2>Upload 3D Model</h2>
    
    <div v-if="error" class="error-message">{{ error }}</div>
    
    <form @submit.prevent="uploadModel" class="upload-form">
      <div class="form-group">
        <label for="model-file-input">Select 3D Model File:</label>
        <input 
          type="file" 
          id="model-file-input"
          @change="handleFileChange"
          accept=".obj,.gltf,.glb,.fbx"
        />
        <p class="help-text">Supported formats: OBJ, GLTF, GLB, FBX</p>
      </div>
      
      <div class="form-group">
        <label for="model-name">Model Name:</label>
        <input 
          type="text" 
          id="model-name"
          v-model="modelName"
          placeholder="Enter a name for your model"
          required
        />
      </div>
      
      <div class="form-group">
        <label for="model-description">Description (optional):</label>
        <textarea 
          id="model-description"
          v-model="modelDescription"
          placeholder="Enter a description for your model"
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-actions">
        <button 
          type="button" 
          @click="cancelUpload" 
          class="cancel-button"
          :disabled="isUploading"
        >
          Cancel
        </button>
        <button 
          type="submit" 
          class="upload-button"
          :disabled="isUploading || !selectedFile"
        >
          {{ isUploading ? 'Uploading...' : 'Upload Model' }}
        </button>
      </div>
      
      <div v-if="isUploading" class="progress-container">
        <div class="progress-bar" :style="{ width: `${uploadProgress}%` }"></div>
        <span class="progress-text">{{ uploadProgress }}%</span>
      </div>
    </form>
  </div>
</template>

<style scoped>
.model-uploader {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.upload-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: bold;
  color: #555;
}

input[type="text"],
textarea {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input[type="file"] {
  padding: 0.5rem 0;
}

.help-text {
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.upload-button,
.cancel-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.upload-button {
  background-color: #4CAF50;
  color: white;
}

.upload-button:hover:not(:disabled) {
  background-color: #45a049;
}

.cancel-button {
  background-color: #f44336;
  color: white;
}

.cancel-button:hover:not(:disabled) {
  background-color: #d32f2f;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.progress-container {
  height: 1.25rem;
  background-color: #eee;
  border-radius: 4px;
  margin-top: 1rem;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #4CAF50;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #333;
  font-size: 0.8rem;
  font-weight: bold;
}

.error-message {
  background-color: #ffebee;
  color: #f44336;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border-left: 4px solid #f44336;
}
</style>
