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

  updateModel(id, data) {
    if (!id) {
      return Promise.reject(new Error('Model ID is required'));
    }
    return apiClient.post(`/api/models/${id}/update`, data);
  },

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
  },

  // Drawing related API calls
  executeDrawingSession(sessionData) {
    return apiClient.post('/api/draw/session', sessionData);
  },
  
  drawLine(points, color = '#ffffff', thickness = 0.01, name = 'Line') {
    return apiClient.post('/api/draw/line', {
      points,
      color,
      thickness,
      name
    });
  },
  
  drawPrimitive(primitiveType, location = [0, 0, 0], scale = [1, 1, 1], color = '#8080ff', name = null) {
    return apiClient.post('/api/draw/primitive', {
      primitive_type: primitiveType,
      location,
      scale,
      color,
      name: name || `${primitiveType.charAt(0).toUpperCase() + primitiveType.slice(1)}_Generated`
    });
  },

  drawCustomCoords(coordinatesText, color = '#cccccc', name = 'CustomMesh', useConvexHull = true) {
    // Handle both string and points array formats
    let coordinatesData;
    if (typeof coordinatesText === 'string') {
      coordinatesData = coordinatesText;
    } else if (Array.isArray(coordinatesText)) {
      // Convert points array to text format - ensure proper number formatting
      coordinatesData = coordinatesText.map(p => `${parseFloat(p.x)} ${parseFloat(p.y)} ${parseFloat(p.z)}`).join('\n');
    } else {
      return Promise.reject(new Error('Invalid coordinates format'));
    }
    
    // Validate that we have at least 3 points
    const lines = coordinatesData.split('\n').filter(line => line.trim().length > 0);
    if (lines.length < 3) {
      return Promise.reject(new Error('At least 3 coordinate points are required'));
    }
    
    return apiClient.post('/api/draw/custom-coords', {
      coordinates_text: coordinatesData,
      color,
      name,
      use_convex_hull: useConvexHull
    });
  }
};
