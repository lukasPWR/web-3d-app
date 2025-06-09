<template>
  <div class="model-analyzer">
    <div class="analyzer-header">
      <h3>Model Analyzer & Descriptor</h3>
      <button @click="toggleAnalyzer" class="toggle-btn">
        {{ showAnalyzer ? 'Hide' : 'Show' }} Details
      </button>
    </div>
    
    <div v-if="showAnalyzer" class="analyzer-content">
      <!-- Model Selection -->
      <div class="section">
        <h4>Select Model to Analyze</h4>
        <select v-model="selectedModelId" @change="analyzeSelectedModel" class="model-selector">
          <option value="">Choose a model...</option>
          <option v-for="[modelId, model] in loadedModels" :key="modelId" :value="modelId">
            {{ model.userData.modelName || `Model ${modelId}` }}
          </option>
        </select>
      </div>
      
      <!-- Model Analysis Results -->
      <div v-if="selectedModelId && analysisData" class="section">
        <h4>Technical Analysis</h4>
        <div class="analysis-grid">
          <div class="stat-card">
            <label>Total Meshes:</label>
            <span class="stat-value">{{ analysisData.meshCount }}</span>
          </div>
          
          <div class="stat-card">
            <label>Total Vertices:</label>
            <span class="stat-value">{{ analysisData.totalVertices.toLocaleString() }}</span>
          </div>
          
          <div class="stat-card">
            <label>Total Faces:</label>
            <span class="stat-value">{{ analysisData.totalFaces.toLocaleString() }}</span>
          </div>
          
          <div class="stat-card">
            <label>Materials:</label>
            <span class="stat-value">{{ analysisData.materialCount }}</span>
          </div>
          
          <div class="stat-card">
            <label>Bounding Box:</label>
            <span class="stat-value">
              {{ analysisData.boundingBox.size.x.toFixed(2) }} × 
              {{ analysisData.boundingBox.size.y.toFixed(2) }} × 
              {{ analysisData.boundingBox.size.z.toFixed(2) }}
            </span>
          </div>
          
          <div class="stat-card">
            <label>Memory Usage:</label>
            <span class="stat-value">{{ formatBytes(analysisData.memoryUsage) }}</span>
          </div>
        </div>
        
        <!-- Detailed Mesh Information -->
        <div class="mesh-details">
          <h5>Mesh Details</h5>
          <div class="mesh-list">
            <div v-for="(mesh, index) in analysisData.meshes" :key="index" class="mesh-item">
              <strong>Mesh {{ index + 1 }}:</strong>
              <span>{{ mesh.vertices }} vertices, {{ mesh.faces }} faces</span>
              <span v-if="mesh.name">({{ mesh.name }})</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Vertex Analysis Section -->
      <div v-if="selectedModelId && analysisData" class="section">
        <h4>Vertex Analysis</h4>
        <div class="vertex-analysis">
          <div class="vertex-stats">
            <div class="stat-row">
              <label>Average Vertices per Mesh:</label>
              <span>{{ Math.round(analysisData.totalVertices / analysisData.meshCount) }}</span>
            </div>
            <div class="stat-row">
              <label>Vertex Density:</label>
              <span>{{ getVertexDensity() }} vertices/unit³</span>
            </div>
            <div class="stat-row">
              <label>Mesh Quality:</label>
              <span class="quality-indicator" :class="getMeshQualityClass()">
                {{ getMeshQuality() }}
              </span>
            </div>
          </div>
          
          <!-- Vertex Distribution Chart -->
          <div class="vertex-distribution">
            <h5>Vertex Distribution by Mesh</h5>
            <div class="chart-container">
              <div 
                v-for="(mesh, index) in analysisData.meshes" 
                :key="index"
                class="chart-bar"
                :style="{ 
                  height: `${(mesh.vertices / analysisData.maxVerticesInMesh) * 100}px`,
                  backgroundColor: getBarColor(mesh.vertices / analysisData.maxVerticesInMesh)
                }"
                :title="`Mesh ${index + 1}: ${mesh.vertices} vertices`"
              ></div>
            </div>
            <div class="chart-labels">
              <span>Mesh Distribution</span>
              <small>Height = vertex count</small>
            </div>
          </div>
          
          <!-- Geometry Analysis -->
          <div class="geometry-analysis">
            <h5>Geometry Complexity</h5>
            <div class="complexity-grid">
              <div class="complexity-item">
                <label>Triangle to Vertex Ratio:</label>
                <span>{{ getTriangleVertexRatio() }}</span>
                <small>{{ getTriangleVertexRatioDescription() }}</small>
              </div>
              
              <div class="complexity-item">
                <label>Average Face Size:</label>
                <span>{{ getAverageFaceSize() }} units²</span>
                <small>Based on bounding box estimation</small>
              </div>
              
              <div class="complexity-item">
                <label>Model Resolution:</label>
                <span class="resolution-indicator" :class="getResolutionClass()">
                  {{ getModelResolution() }}
                </span>
                <small>{{ getResolutionDescription() }}</small>
              </div>
            </div>
          </div>
          
          <!-- Performance Metrics -->
          <div class="performance-metrics">
            <h5>Performance Impact</h5>
            <div class="performance-grid">
              <div class="perf-metric" :class="getRenderingPerformanceClass()">
                <label>Rendering Performance:</label>
                <span>{{ getRenderingPerformance() }}</span>
              </div>
              
              <div class="perf-metric" :class="getMemoryUsageClass()">
                <label>Memory Impact:</label>
                <span>{{ getMemoryImpact() }}</span>
              </div>
              
              <div class="perf-metric" :class="getOptimizationClass()">
                <label>Optimization Level:</label>
                <span>{{ getOptimizationLevel() }}</span>
              </div>
            </div>
            
            <!-- Optimization Suggestions -->
            <div class="optimization-suggestions">
              <h6>Optimization Suggestions:</h6>
              <ul class="suggestions-list">
                <li v-for="suggestion in getOptimizationSuggestions()" :key="suggestion">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Model Description Interface -->
      <div v-if="selectedModelId" class="section">
        <h4>Model Description</h4>
        <div class="description-form">
          <div class="form-group">
            <label for="model-title">Title:</label>
            <input 
              type="text" 
              id="model-title"
              v-model="modelDescription.title"
              placeholder="Enter model title"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="model-description">Description:</label>
            <textarea 
              id="model-description"
              v-model="modelDescription.description"
              placeholder="Describe the model..."
              rows="3"
              class="form-input"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="model-category">Category:</label>
            <select v-model="modelDescription.category" id="model-category" class="form-input">
              <option value="">Select category...</option>
              <option value="furniture">Furniture</option>
              <option value="vehicle">Vehicle</option>
              <option value="building">Building</option>
              <option value="character">Character</option>
              <option value="weapon">Weapon</option>
              <option value="tool">Tool</option>
              <option value="decoration">Decoration</option>
              <option value="nature">Nature</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="model-tags">Tags:</label>
            <input 
              type="text" 
              id="model-tags"
              v-model="modelDescription.tags"
              placeholder="Enter tags separated by commas"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="complexity-level">Complexity Level:</label>
            <select v-model="modelDescription.complexity" id="complexity-level" class="form-input">
              <option value="low">Low (< 1K vertices)</option>
              <option value="medium">Medium (1K - 10K vertices)</option>
              <option value="high">High (10K - 100K vertices)</option>
              <option value="very-high">Very High (> 100K vertices)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="model-scale">Real-world Scale:</label>
            <div class="scale-inputs">
              <input 
                type="number" 
                v-model.number="modelDescription.realWorldSize.length"
                placeholder="Length"
                class="scale-input"
                step="0.1"
                min="0"
              />
              <span>×</span>
              <input 
                type="number" 
                v-model.number="modelDescription.realWorldSize.width"
                placeholder="Width"
                class="scale-input"
                step="0.1"
                min="0"
              />
              <span>×</span>
              <input 
                type="number" 
                v-model.number="modelDescription.realWorldSize.height"
                placeholder="Height"
                class="scale-input"
                step="0.1"
                min="0"
              />
              <select v-model="modelDescription.realWorldSize.unit" class="unit-select">
                <option value="mm">mm</option>
                <option value="cm">cm</option>
                <option value="m">m</option>
                <option value="in">inches</option>
                <option value="ft">feet</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                v-model="modelDescription.isAnimated"
              />
              Model has animations
            </label>
          </div>
          
          <div class="form-group">
            <label>
              <input 
                type="checkbox" 
                v-model="modelDescription.hasTextures"
              />
              Model has textures
            </label>
          </div>
          
          <div class="form-actions">
            <button @click="saveModelDescription" class="save-btn" :disabled="!canSave">
              Save Description
            </button>
            <button @click="loadModelDescription" class="load-btn" v-if="hasExistingDescription">
              Load Saved Description
            </button>
            <button @click="clearDescription" class="clear-btn">
              Clear
            </button>
          </div>
        </div>
      </div>
      
      <!-- Saved Descriptions -->
      <div v-if="savedDescriptions.length > 0" class="section">
        <h4>Saved Descriptions</h4>
        <div class="saved-descriptions">
          <div v-for="desc in savedDescriptions" :key="desc.id" class="description-card">
            <div class="description-header">
              <h5>{{ desc.title || 'Untitled' }}</h5>
              <span class="description-date">{{ formatDate(desc.savedAt) }}</span>
            </div>
            <p class="description-text">{{ desc.description || 'No description' }}</p>
            <div class="description-meta">
              <span class="tag">{{ desc.category }}</span>
              <span class="complexity">{{ desc.complexity }} complexity</span>
            </div>
            <div class="description-actions">
              <button @click="loadDescription(desc)" class="load-btn small">Load</button>
              <button @click="deleteDescription(desc.id)" class="delete-btn small">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, inject, watch } from 'vue';
import * as THREE from 'three';

export default {
  name: 'ModelAnalyzer',
  setup() {
    const showAnalyzer = ref(false);
    const selectedModelId = ref('');
    const analysisData = ref(null);
    const savedDescriptions = ref([]);
    
    // Get loaded models from parent
    const threeScene = inject('threeScene', null);
    const loadedModels = threeScene?.loadedModels || new Map();
    
    // Model description form
    const modelDescription = reactive({
      title: '',
      description: '',
      category: '',
      tags: '',
      complexity: '',
      realWorldSize: {
        length: null,
        width: null,
        height: null,
        unit: 'm'
      },
      isAnimated: false,
      hasTextures: false
    });
    
    const toggleAnalyzer = () => {
      showAnalyzer.value = !showAnalyzer.value;
    };
    
    // Analyze selected model
    const analyzeSelectedModel = () => {
      if (!selectedModelId.value || !loadedModels.has(selectedModelId.value)) {
        analysisData.value = null;
        return;
      }
      
      const model = loadedModels.get(selectedModelId.value);
      analysisData.value = analyzeModel(model);
      
      // Auto-set complexity based on vertex count
      if (analysisData.value.totalVertices < 1000) {
        modelDescription.complexity = 'low';
      } else if (analysisData.value.totalVertices < 10000) {
        modelDescription.complexity = 'medium';
      } else if (analysisData.value.totalVertices < 100000) {
        modelDescription.complexity = 'high';
      } else {
        modelDescription.complexity = 'very-high';
      }
      
      // Auto-detect textures
      modelDescription.hasTextures = analysisData.value.hasTextures;
    };
    
    // Analyze model function
    const analyzeModel = (model) => {
      const analysis = {
        meshCount: 0,
        totalVertices: 0,
        totalFaces: 0,
        materialCount: 0,
        memoryUsage: 0,
        meshes: [],
        materials: new Set(),
        hasTextures: false,
        boundingBox: {
          min: new THREE.Vector3(),
          max: new THREE.Vector3(),
          size: new THREE.Vector3(),
          center: new THREE.Vector3()
        },
        maxVerticesInMesh: 0,
        minVerticesInMesh: Infinity,
        meshDetails: []
      };
      
      // Calculate bounding box
      const box = new THREE.Box3().setFromObject(model);
      analysis.boundingBox.min = box.min;
      analysis.boundingBox.max = box.max;
      box.getSize(analysis.boundingBox.size);
      box.getCenter(analysis.boundingBox.center);
      
      // Traverse model and collect data
      model.traverse((child) => {
        if (child.isMesh) {
          analysis.meshCount++;
          
          const geometry = child.geometry;
          if (geometry) {
            const vertices = geometry.attributes.position ? 
              geometry.attributes.position.count : 0;
            const faces = geometry.index ? 
              geometry.index.count / 3 : vertices / 3;
            
            analysis.totalVertices += vertices;
            analysis.totalFaces += Math.floor(faces);
            
            // Estimate memory usage (rough calculation)
            analysis.memoryUsage += vertices * 12; // 3 floats * 4 bytes per vertex
            if (geometry.attributes.normal) {
              analysis.memoryUsage += vertices * 12;
            }
            if (geometry.attributes.uv) {
              analysis.memoryUsage += vertices * 8; // 2 floats * 4 bytes per UV
            }
            if (geometry.index) {
              analysis.memoryUsage += geometry.index.count * 4; // 4 bytes per index
            }
            
            const meshDetail = {
              name: child.name || 'Unnamed',
              vertices: vertices,
              faces: Math.floor(faces),
              geometry: geometry,
              boundingBox: new THREE.Box3().setFromObject(child)
            };
            
            analysis.meshes.push(meshDetail);
            analysis.meshDetails.push(meshDetail);
            analysis.maxVerticesInMesh = Math.max(analysis.maxVerticesInMesh, vertices);
            analysis.minVerticesInMesh = Math.min(analysis.minVerticesInMesh, vertices);
          }
          
          // Check materials
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(mat => {
                analysis.materials.add(mat.uuid);
                if (mat.map || mat.normalMap || mat.roughnessMap || mat.metalnessMap) {
                  analysis.hasTextures = true;
                }
              });
            } else {
              analysis.materials.add(child.material.uuid);
              if (child.material.map || child.material.normalMap || 
                  child.material.roughnessMap || child.material.metalnessMap) {
                analysis.hasTextures = true;
              }
            }
          }
        }
      });
      
      analysis.materialCount = analysis.materials.size;
      
      return analysis;
    };
    
    // Format bytes
    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Format date
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };
    
    // Save model description
    const saveModelDescription = () => {
      if (!selectedModelId.value) return;
      
      const description = {
        id: `desc_${selectedModelId.value}_${Date.now()}`,
        modelId: selectedModelId.value,
        title: modelDescription.title,
        description: modelDescription.description,
        category: modelDescription.category,
        tags: modelDescription.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        complexity: modelDescription.complexity,
        realWorldSize: { ...modelDescription.realWorldSize },
        isAnimated: modelDescription.isAnimated,
        hasTextures: modelDescription.hasTextures,
        technicalData: analysisData.value,
        savedAt: new Date().toISOString()
      };
      
      // Save to localStorage
      const saved = JSON.parse(localStorage.getItem('modelDescriptions') || '[]');
      saved.push(description);
      localStorage.setItem('modelDescriptions', JSON.stringify(saved));
      
      // Update local list
      savedDescriptions.value = saved;
      
      alert('Model description saved successfully!');
    };
    
    // Load saved descriptions
    const loadSavedDescriptions = () => {
      const saved = JSON.parse(localStorage.getItem('modelDescriptions') || '[]');
      savedDescriptions.value = saved;
    };
    
    // Load specific description
    const loadDescription = (desc) => {
      Object.assign(modelDescription, {
        title: desc.title,
        description: desc.description,
        category: desc.category,
        tags: desc.tags.join(', '),
        complexity: desc.complexity,
        realWorldSize: { ...desc.realWorldSize },
        isAnimated: desc.isAnimated,
        hasTextures: desc.hasTextures
      });
    };
    
    // Delete description
    const deleteDescription = (id) => {
      if (confirm('Are you sure you want to delete this description?')) {
        const saved = savedDescriptions.value.filter(desc => desc.id !== id);
        localStorage.setItem('modelDescriptions', JSON.stringify(saved));
        savedDescriptions.value = saved;
      }
    };
    
    // Clear form
    const clearDescription = () => {
      Object.assign(modelDescription, {
        title: '',
        description: '',
        category: '',
        tags: '',
        complexity: '',
        realWorldSize: {
          length: null,
          width: null,
          height: null,
          unit: 'm'
        },
        isAnimated: false,
        hasTextures: false
      });
    };
    
    // Computed properties
    const canSave = computed(() => {
      return selectedModelId.value && (
        modelDescription.title || 
        modelDescription.description || 
        modelDescription.category
      );
    });
    
    const hasExistingDescription = computed(() => {
      return savedDescriptions.value.some(desc => desc.modelId === selectedModelId.value);
    });
    
    // NEW: Vertex analysis functions
    const getVertexDensity = () => {
      if (!analysisData.value) return 0;
      
      const volume = analysisData.value.boundingBox.size.x * 
                    analysisData.value.boundingBox.size.y * 
                    analysisData.value.boundingBox.size.z;
      
      return volume > 0 ? Math.round(analysisData.value.totalVertices / volume) : 0;
    };
    
    const getMeshQuality = () => {
      if (!analysisData.value) return 'Unknown';
      
      const avgVertices = analysisData.value.totalVertices / analysisData.value.meshCount;
      
      if (avgVertices < 100) return 'Low Poly';
      if (avgVertices < 1000) return 'Medium Poly';
      if (avgVertices < 10000) return 'High Poly';
      return 'Very High Poly';
    };
    
    const getMeshQualityClass = () => {
      const quality = getMeshQuality();
      switch (quality) {
        case 'Low Poly': return 'quality-low';
        case 'Medium Poly': return 'quality-medium';
        case 'High Poly': return 'quality-high';
        case 'Very High Poly': return 'quality-very-high';
        default: return '';
      }
    };
    
    const getBarColor = (ratio) => {
      const hue = (1 - ratio) * 120; // Green to red
      return `hsl(${hue}, 70%, 50%)`;
    };
    
    const getTriangleVertexRatio = () => {
      if (!analysisData.value) return '0:1';
      
      const ratio = analysisData.value.totalFaces / analysisData.value.totalVertices;
      return `${ratio.toFixed(2)}:1`;
    };
    
    const getTriangleVertexRatioDescription = () => {
      const ratio = analysisData.value?.totalFaces / analysisData.value?.totalVertices || 0;
      
      if (ratio < 0.5) return 'Low triangle density - may appear blocky';
      if (ratio < 1.5) return 'Good triangle distribution';
      return 'High triangle density - smooth but performance heavy';
    };
    
    const getAverageFaceSize = () => {
      if (!analysisData.value) return 0;
      
      const totalSurfaceArea = analysisData.value.boundingBox.size.x * 
                              analysisData.value.boundingBox.size.y * 2 +
                              analysisData.value.boundingBox.size.y * 
                              analysisData.value.boundingBox.size.z * 2 +
                              analysisData.value.boundingBox.size.x * 
                              analysisData.value.boundingBox.size.z * 2;
      
      return (totalSurfaceArea / analysisData.value.totalFaces).toFixed(4);
    };
    
    const getModelResolution = () => {
      if (!analysisData.value) return 'Unknown';
      
      const vertices = analysisData.value.totalVertices;
      
      if (vertices < 500) return 'Very Low';
      if (vertices < 2000) return 'Low';
      if (vertices < 10000) return 'Medium';
      if (vertices < 50000) return 'High';
      return 'Very High';
    };
    
    const getResolutionClass = () => {
      const resolution = getModelResolution();
      switch (resolution) {
        case 'Very Low': return 'resolution-very-low';
        case 'Low': return 'resolution-low';
        case 'Medium': return 'resolution-medium';
        case 'High': return 'resolution-high';
        case 'Very High': return 'resolution-very-high';
        default: return '';
      }
    };
    
    const getResolutionDescription = () => {
      const resolution = getModelResolution();
      const descriptions = {
        'Very Low': 'Suitable for distant objects or mobile games',
        'Low': 'Good for background objects or simple shapes',
        'Medium': 'Balanced quality for most applications',
        'High': 'Detailed model suitable for close-up viewing',
        'Very High': 'Extremely detailed - may impact performance'
      };
      return descriptions[resolution] || '';
    };
    
    const getRenderingPerformance = () => {
      if (!analysisData.value) return 'Unknown';
      
      const vertices = analysisData.value.totalVertices;
      
      if (vertices < 1000) return 'Excellent';
      if (vertices < 5000) return 'Good';
      if (vertices < 20000) return 'Fair';
      return 'Poor';
    };
    
    const getRenderingPerformanceClass = () => {
      const performance = getRenderingPerformance();
      switch (performance) {
        case 'Excellent': return 'perf-excellent';
        case 'Good': return 'perf-good';
        case 'Fair': return 'perf-fair';
        case 'Poor': return 'perf-poor';
        default: return '';
      }
    };
    
    const getMemoryImpact = () => {
      if (!analysisData.value) return 'Unknown';
      
      const memory = analysisData.value.memoryUsage;
      
      if (memory < 100000) return 'Low'; // < 100KB
      if (memory < 1000000) return 'Medium'; // < 1MB
      if (memory < 10000000) return 'High'; // < 10MB
      return 'Very High';
    };
    
    const getMemoryUsageClass = () => {
      const impact = getMemoryImpact();
      switch (impact) {
        case 'Low': return 'memory-low';
        case 'Medium': return 'memory-medium';
        case 'High': return 'memory-high';
        case 'Very High': return 'memory-very-high';
        default: return '';
      }
    };
    
    const getOptimizationLevel = () => {
      if (!analysisData.value) return 'Unknown';
      
      const ratio = analysisData.value.totalFaces / analysisData.value.totalVertices;
      const meshCount = analysisData.value.meshCount;
      
      let score = 0;
      
      // Good triangle to vertex ratio
      if (ratio >= 0.8 && ratio <= 1.2) score += 2;
      else if (ratio >= 0.6 && ratio <= 1.5) score += 1;
      
      // Reasonable mesh count
      if (meshCount <= 10) score += 2;
      else if (meshCount <= 25) score += 1;
      
      // Memory efficiency
      const memoryPerVertex = analysisData.value.memoryUsage / analysisData.value.totalVertices;
      if (memoryPerVertex < 50) score += 2;
      else if (memoryPerVertex < 100) score += 1;
      
      if (score >= 5) return 'Excellent';
      if (score >= 3) return 'Good';
      if (score >= 1) return 'Fair';
      return 'Poor';
    };
    
    const getOptimizationClass = () => {
      const level = getOptimizationLevel();
      switch (level) {
        case 'Excellent': return 'opt-excellent';
        case 'Good': return 'opt-good';
        case 'Fair': return 'opt-fair';
        case 'Poor': return 'opt-poor';
        default: return '';
      }
    };
    
    const getOptimizationSuggestions = () => {
      if (!analysisData.value) return [];
      
      const suggestions = [];
      
      if (analysisData.value.totalVertices > 50000) {
        suggestions.push('Consider using LOD (Level of Detail) for better performance');
      }
      
      if (analysisData.value.meshCount > 20) {
        suggestions.push('Merge similar meshes to reduce draw calls');
      }
      
      const ratio = analysisData.value.totalFaces / analysisData.value.totalVertices;
      if (ratio > 2) {
        suggestions.push('High triangle density detected - consider mesh decimation');
      }
      
      if (analysisData.value.memoryUsage > 5000000) { // 5MB
        suggestions.push('Large memory footprint - consider texture compression');
      }
      
      if (!analysisData.value.hasTextures && analysisData.value.totalVertices > 10000) {
        suggestions.push('Add textures to reduce vertex count for detail');
      }
      
      if (suggestions.length === 0) {
        suggestions.push('Model appears well optimized for real-time rendering');
      }
      
      return suggestions;
    };
    
    // Load saved descriptions on mount
    loadSavedDescriptions();
    
    return {
      showAnalyzer,
      selectedModelId,
      analysisData,
      modelDescription,
      savedDescriptions,
      loadedModels,
      toggleAnalyzer,
      analyzeSelectedModel,
      formatBytes,
      formatDate,
      saveModelDescription,
      loadDescription,
      deleteDescription,
      clearDescription,
      canSave,
      hasExistingDescription,
      getVertexDensity,
      getMeshQuality,
      getMeshQualityClass,
      getBarColor,
      getTriangleVertexRatio,
      getTriangleVertexRatioDescription,
      getAverageFaceSize,
      getModelResolution,
      getResolutionClass,
      getResolutionDescription,
      getRenderingPerformance,
      getRenderingPerformanceClass,
      getMemoryImpact,
      getMemoryUsageClass,
      getOptimizationLevel,
      getOptimizationClass,
      getOptimizationSuggestions
    };
  }
};
</script>

<style scoped>
.model-analyzer {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 10px 0;
}

.analyzer-header {
  padding: 15px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e9ecef;
  border-radius: 8px 8px 0 0;
}

.analyzer-header h3 {
  margin: 0;
  color: #333;
}

.toggle-btn {
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.toggle-btn:hover {
  background-color: #0056b3;
}

.analyzer-content {
  padding: 20px;
}

.section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.section:last-child {
  border-bottom: none;
}

.section h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
}

.model-selector {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.stat-card {
  background-color: white;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card label {
  font-weight: bold;
  color: #666;
  font-size: 12px;
}

.stat-value {
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.mesh-details h5 {
  margin: 15px 0 10px 0;
  color: #333;
}

.mesh-list {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  max-height: 150px;
  overflow-y: auto;
}

.mesh-item {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
  font-size: 12px;
}

.mesh-item:last-child {
  border-bottom: none;
}

.description-form {
  background-color: white;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
  font-size: 13px;
}

.form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.scale-inputs {
  display: flex;
  align-items: center;
  gap: 5px;
}

.scale-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.unit-select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.save-btn, .load-btn, .clear-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;
}

.save-btn {
  background-color: #28a745;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background-color: #218838;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.load-btn {
  background-color: #007bff;
  color: white;
}

.load-btn:hover {
  background-color: #0056b3;
}

.clear-btn {
  background-color: #6c757d;
  color: white;
}

.clear-btn:hover {
  background-color: #545b62;
}

.saved-descriptions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
}

.description-card {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
}

.description-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.description-header h5 {
  margin: 0;
  color: #333;
}

.description-date {
  font-size: 11px;
  color: #666;
}

.description-text {
  margin: 10px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
}

.description-meta {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.tag {
  background-color: #e9ecef;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  color: #333;
}

.complexity {
  background-color: #fff3cd;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  color: #856404;
}

.description-actions {
  display: flex;
  gap: 5px;
  margin-top: 10px;
}

.small {
  padding: 4px 8px;
  font-size: 11px;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #c82333;
}

.vertex-analysis {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
}

.vertex-stats {
  margin-bottom: 20px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.stat-row:last-child {
  border-bottom: none;
}

.quality-indicator, .resolution-indicator {
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: bold;
  font-size: 11px;
}

.quality-low, .resolution-very-low, .resolution-low { 
  background-color: #ffcdd2; 
  color: #c62828; 
}

.quality-medium, .resolution-medium { 
  background-color: #fff3e0; 
  color: #f57c00; 
}

.quality-high, .resolution-high { 
  background-color: #e8f5e8; 
  color: #2e7d32; 
}

.quality-very-high, .resolution-very-high { 
  background-color: #e3f2fd; 
  color: #1565c0; 
}

.vertex-distribution {
  margin: 20px 0;
}

.chart-container {
  display: flex;
  align-items: end;
  height: 100px;
  gap: 2px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.chart-bar {
  flex: 1;
  min-height: 5px;
  border-radius: 2px 2px 0 0;
  transition: opacity 0.2s;
}

.chart-bar:hover {
  opacity: 0.7;
}

.chart-labels {
  text-align: center;
  margin-top: 5px;
  font-size: 11px;
  color: #666;
}

.complexity-grid, .performance-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
  margin: 15px 0;
}

.complexity-item, .perf-metric {
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.complexity-item label, .perf-metric label {
  font-weight: bold;
  display: block;
  margin-bottom: 5px;
}

.complexity-item small {
  display: block;
  color: #666;
  font-size: 10px;
  margin-top: 3px;
}

.perf-excellent { border-left: 4px solid #4caf50; }
.perf-good { border-left: 4px solid #8bc34a; }
.perf-fair { border-left: 4px solid #ff9800; }
.perf-poor { border-left: 4px solid #f44336; }

.memory-low { background-color: #e8f5e8; }
.memory-medium { background-color: #fff3e0; }
.memory-high { background-color: #ffebee; }
.memory-very-high { background-color: #ffcdd2; }

.opt-excellent { background-color: #e8f5e8; }
.opt-good { background-color: #f1f8e9; }
.opt-fair { background-color: #fff8e1; }
.opt-poor { background-color: #ffebee; }

.optimization-suggestions {
  margin-top: 15px;
  padding: 10px;
  background-color: #e3f2fd;
  border-radius: 4px;
}

.optimization-suggestions h6 {
  margin: 0 0 8px 0;
  color: #1565c0;
}

.suggestions-list {
  margin: 0;
  padding-left: 15px;
  color: #1976d2;
}

.suggestions-list li {
  margin-bottom: 3px;
  font-size: 12px;
}
</style>
