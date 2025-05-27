import axios from 'axios';

// Configure Axios defaults
axios.defaults.timeout = 10000;

const apiClient = axios.create({
  baseURL: '/',  // This will use the proxy set up in vite.config.js
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    // Log errors to console
    console.error('API Error:', error);
    
    // Add additional error handling logic here if needed
    if (error.response && error.response.status === 404) {
      console.error('Resource not found:', error.config.url);
    }
    
    return Promise.reject(error);
  }
);

export default {
  // Model related API calls
  getModels() {
    return apiClient.get('/api/models');
  },
  
  getModel(id) {
    if (!id) {
      return Promise.reject(new Error('Model ID is required'));
    }
    return apiClient.get(`/api/models/${id}`);
  },
  
  uploadModel(formData) {
    return apiClient.post('/api/models/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  deleteModel(id) {
    if (!id) {
      return Promise.reject(new Error('Model ID is required'));
    }
    return apiClient.delete(`/api/models/${id}`);
  },

  // Texture related API calls
  getTextures() {
    return apiClient.get('/api/textures');
  },
  
  uploadTexture(formData) {
    return apiClient.post('/api/textures/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  deleteTexture(id) {
    if (!id) {
      return Promise.reject(new Error('Texture ID is required'));
    }
    return apiClient.delete(`/api/textures/${id}`);
  }
};
