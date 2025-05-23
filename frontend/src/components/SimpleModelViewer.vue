<template>
  <div class="model-viewer-container">
    <div id="modelViewer" ref="container"></div>
    <div v-if="isLoading" class="loading-overlay">
      <p>Loading models...</p>
    </div>
    
    <div class="scene-controls">
      <button @click="resetCamera" class="control-button">Reset View</button>
      <button @click="toggleGrid" class="control-button">{{ showGrid ? 'Hide' : 'Show' }} Grid</button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';

export default {
  name: 'SimpleModelViewer',
  props: {
    // Array of model objects with { id, modelPath, color, position, scale, rotation }
    models: {
      type: Array,
      required: false,
      default: () => []
    },
    // For backwards compatibility - single model path
    modelPath: {
      type: String,
      required: false
    },
    // For backwards compatibility - single model format
    modelFormat: {
      type: String,
      required: false
    }
  },
  setup(props) {
    const container = ref(null);
    const isLoading = ref(true);
    const showGrid = ref(true);
    
    // Create a computed prop that handles both the new models array and the legacy modelPath/modelFormat props
    const modelsToLoad = computed(() => {
      // If models array is provided and not empty, use it
      if (props.models && Array.isArray(props.models) && props.models.length > 0) {
        return props.models;
      }
      
      // If modelPath is provided, create a single-item array with that model
      if (props.modelPath) {
        return [{
          id: 'legacy-model',
          modelPath: props.modelPath,
          format: props.modelFormat
        }];
      }
      
      // Default to empty array
      return [];
    });

    // Scene objects
    let scene, camera, renderer, controls, gridHelper;
    let animationFrameId = null; // Track animation frame ID
    
    // Map to track loaded models - key: modelId, value: THREE.Object3D
    const loadedModels = reactive(new Map());
    
    // Initialize Three.js scene
    const initScene = () => {
      // Clean up any previous scene first
      cleanupThreeJS();
      
      // Create scene
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0xf0f0f0);
      
      // Create camera
      camera = new THREE.PerspectiveCamera(
        45,
        container.value.clientWidth / container.value.clientHeight,
        0.1,
        1000
      );
      camera.position.set(10, 10, 10);
      
      // Create renderer with better options for WebGL stability
      renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        powerPreference: 'default',
        failIfMajorPerformanceCaveat: false
      });
      renderer.setSize(container.value.clientWidth, container.value.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // Limit pixel ratio
      renderer.shadowMap.enabled = true;
      
      // Check if container already has a canvas and remove it
      const existingCanvas = container.value.querySelector('canvas');
      if (existingCanvas) {
        container.value.removeChild(existingCanvas);
      }
      
      container.value.appendChild(renderer.domElement);
      
      // Add lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);
      
      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(5, 10, 7.5);
      directionalLight.castShadow = true;
      scene.add(directionalLight);
      
      // Add hemisphere light for better ambient illumination
      const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
      hemiLight.position.set(0, 20, 0);
      scene.add(hemiLight);
      
      // Add orbit controls
      controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      
      // Add grid helper
      addGrid();
      
      // Start animation loop
      animate();
    };
    
    // Add grid to the scene
    const addGrid = () => {
      if (!gridHelper) {
        gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
        scene.add(gridHelper);
      }
    };
    
    // Toggle grid visibility
    const toggleGrid = () => {
      if (gridHelper) {
        showGrid.value = !showGrid.value;
        gridHelper.visible = showGrid.value;
      }
    };
    
    // Reset camera to initial position
    const resetCamera = () => {
      camera.position.set(10, 10, 10);
      controls.target.set(0, 0, 0);
      controls.update();
    };
    
    // Load a model
    const loadModel = async (modelData) => {
      // Get the model path - supporting both modelPath and modelUrl properties
      const modelPath = modelData.modelPath || modelData.modelUrl;
      
      if (!modelData || !modelData.id || (!modelData.modelPath && !modelData.modelUrl)) {
        console.error('Invalid model data provided:', modelData);
        return null;
      }
      
      // If we already loaded this model, remove it first
      if (loadedModels.has(modelData.id)) {
        const existingModel = loadedModels.get(modelData.id);
        scene.remove(existingModel);
        loadedModels.delete(modelData.id);
      }
      
      try {
        const loader = new OBJLoader();
        
        // Load the model with enhanced error handling
        const object = await new Promise((resolve, reject) => {
          loader.load(
            modelPath,
            (obj) => resolve(obj),
            (xhr) => {
              console.log(`${modelData.id}: ${(xhr.loaded / xhr.total) * 100}% loaded`);
            },
            (error) => {
              console.error(`Failed to load model ${modelData.id} from ${modelPath}:`, error);
              reject(error);
            }
          );
        });
        
        // Apply material/color if specified
        if (modelData.color) {
          const material = new THREE.MeshStandardMaterial({ 
            color: new THREE.Color(modelData.color),
            roughness: 0.7,
            metalness: 0.1
          });
          
          object.traverse((child) => {
            if (child.isMesh) {
              child.material = material;
              child.castShadow = true;
              child.receiveShadow = true;
            }
          });
        }
        
        // Apply custom position if available
        if (modelData.position) {
          object.position.set(
            modelData.position.x || 0,
            modelData.position.y || 0, 
            modelData.position.z || 0
          );
        }
        
        // Apply custom scale if available
        if (modelData.scale) {
          const scale = typeof modelData.scale === 'number' 
            ? modelData.scale 
            : modelData.scale.x || 1;
          
          object.scale.set(scale, scale, scale);
        }
        
        // Apply custom rotation if available
        if (modelData.rotation) {
          object.rotation.set(
            THREE.MathUtils.degToRad(modelData.rotation.x || 0),
            THREE.MathUtils.degToRad(modelData.rotation.y || 0),
            THREE.MathUtils.degToRad(modelData.rotation.z || 0)
          );
        }
        
        scene.add(object);
        loadedModels.set(modelData.id, object);
        
        return object;
      } catch (err) {
        console.error(`Error loading model ${modelData.id}:`, err);
        return null;
      }
    };
    
    // Load all models
    const loadModels = async () => {
      isLoading.value = true;
      
      try {
        // Check if models array exists and is not empty
        if (!modelsToLoad.value || modelsToLoad.value.length === 0) {
          console.warn('No models provided or models array is empty');
          isLoading.value = false;
          return;
        }
        
        console.log('Loading models:', modelsToLoad.value); // Debug log
        
        // Process each model in the array
        const loadPromises = modelsToLoad.value.map(model => {
          // Get path from either modelPath or modelUrl
          const modelPath = model.modelPath || model.modelUrl;
          
          // Validate model data before attempting to load
          if (!model || (!model.modelPath && !model.modelUrl)) {
            console.error('Invalid model data:', model);
            return Promise.resolve(null);
          }
          
          // Check if URL is absolute or relative and handle accordingly
          const isAbsoluteUrl = /^(https?:)?\/\//.test(modelPath);
          const modelUrl = isAbsoluteUrl ? modelPath : modelPath;
          
          // Set the model path with corrected URL
          const modelWithFixedPath = {
            ...model,
            modelPath: modelUrl // Always set modelPath for loader to use
          };
          
          return loadModel(modelWithFixedPath);
        });
        
        // Wait for all models to load (or fail)
        await Promise.allSettled(loadPromises);
        
        // Only try to adjust camera if we successfully loaded at least one model
        if (loadedModels.size > 0) {
          fitCameraToModels();
        }
      } catch (err) {
        console.error('Error loading models:', err);
      } finally {
        isLoading.value = false;
      }
    };
    
    // Fit camera to show all models
    const fitCameraToModels = () => {
      if (loadedModels.size === 0) return;
      
      // Create a bounding box that encompasses all models
      const boundingBox = new THREE.Box3();
      
      // Ensure the bounding box is initialized properly
      boundingBox.makeEmpty();
      
      loadedModels.forEach(model => {
        // Temporarily ensure the model's world matrix is updated
        model.updateMatrixWorld(true);
        const modelBox = new THREE.Box3().setFromObject(model);
        
        // Only include valid bounding boxes (non-empty)
        if (!modelBox.isEmpty()) {
          boundingBox.union(modelBox);
        }
      });
      
      // If bounding box is empty or invalid after all calculations, return
      if (boundingBox.isEmpty() || !isFinite(boundingBox.min.x)) {
        console.warn('Unable to calculate valid bounding box for models');
        return;
      }
      
      const center = new THREE.Vector3();
      boundingBox.getCenter(center);
      
      const size = new THREE.Vector3();
      boundingBox.getSize(size);
      
      // Calculate distance to fit all models
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = camera.fov * (Math.PI / 180);
      let distance = maxDim / (2 * Math.tan(fov / 2));
      
      // Add some padding
      distance *= 1.5;
      
      // Position camera to look at center of all models
      const direction = new THREE.Vector3()
        .subVectors(camera.position, controls.target)
        .normalize()
        .multiplyScalar(distance);
      
      camera.position.copy(center).add(direction);
      controls.target.copy(center);
      controls.update();
    };
    
    // Animation loop with proper tracking
    const animate = () => {
      // Cancel any existing animation frame first
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
      }
      
      // Request new animation frame and store the ID
      animationFrameId = requestAnimationFrame(animate);
      
      // Only render if we have valid objects
      if (controls && scene && camera && renderer) {
        controls.update();
        renderer.render(scene, camera);
      }
    };
    
    // Comprehensive cleanup function for Three.js resources
    const cleanupThreeJS = () => {
      // Cancel animation frame if it exists
      if (animationFrameId !== null) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
      
      // Dispose of all loaded models
      if (loadedModels) {
        loadedModels.forEach((model) => {
          if (model) {
            scene?.remove(model);
            model.traverse((child) => {
              if (child.isMesh) {
                if (child.geometry) {
                  child.geometry.dispose();
                }
                if (child.material) {
                  if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                  } else {
                    child.material.dispose();
                  }
                }
              }
            });
          }
        });
        loadedModels.clear();
      }
      
      // Remove grid helper
      if (gridHelper && scene) {
        scene.remove(gridHelper);
        gridHelper = null;
      }
      
      // Dispose of renderer
      if (renderer) {
        renderer.dispose();
        renderer.forceContextLoss();
        
        // Try to free WebGL resources
        const gl = renderer.domElement?.getContext('webgl2') || 
                  renderer.domElement?.getContext('webgl');
        
        if (gl) {
          const loseExt = gl.getExtension('WEBGL_lose_context');
          if (loseExt) {
            loseExt.loseContext();
          }
        }
        
        // Clear renderer reference
        renderer.domElement = null;
        renderer = null;
      }
      
      // Remove canvas from DOM if it exists
      if (container.value) {
        const canvas = container.value.querySelector('canvas');
        if (canvas) {
          container.value.removeChild(canvas);
        }
      }
      
      // Clear other references
      controls = null;
      scene = null;
      camera = null;
    };
    
    // Handle window resize
    const handleResize = () => {
      if (camera && renderer && container.value) {
        camera.aspect = container.value.clientWidth / container.value.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.value.clientWidth, container.value.clientHeight);
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      if (container.value) {
        // Slight delay to ensure DOM is ready
        setTimeout(() => {
          initScene();
          loadModels();
        }, 0);
      }
      
      window.addEventListener('resize', handleResize);
    });
    
    onBeforeUnmount(() => {
      window.removeEventListener('resize', handleResize);
      
      // Properly clean up Three.js resources
      cleanupThreeJS();
    });
    
    // Watch for changes to models array or individual model props
    watch([() => props.models, () => props.modelPath, () => props.modelFormat], () => {
      loadModels();
    }, { deep: true });
    
    return {
      container,
      isLoading,
      showGrid,
      resetCamera,
      toggleGrid
    };
  }
};
</script>

<style scoped>
.model-viewer-container {
  position: relative;
  width: 100%;
  height: 90vh; /* Increased height to 90% of viewport height */
  min-height: 700px; /* Increased minimum height */
  max-width: 100%; /* Ensure it takes full available width */
  margin: 0 auto; /* Center the container */
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Added subtle shadow for depth */
}

#modelViewer {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5em;
  z-index: 10;
}

.scene-controls {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  gap: 8px;
}

.control-button {
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.control-button:hover {
  background-color: rgba(0, 0, 0, 0.7);
}
</style>
