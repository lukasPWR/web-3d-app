<template>
  <div class="model-viewer-wrapper">
    <div class="model-viewer-container">
      <div id="modelViewer" ref="container"></div>
      <div v-if="isLoading" class="loading-overlay">
        <p>Loading models...</p>
      </div>
      
      <div class="scene-controls">
        <button @click="resetCamera" class="control-button">Reset View</button>
        <button @click="toggleGrid" class="control-button">{{ showGrid ? 'Hide' : 'Show' }} Grid</button>
        <button @click="toggleEditMode" class="control-button" :class="{ 'active': editMode }">
          {{ editMode ? 'Exit Edit' : 'Edit Mode' }}
        </button>
      </div>
    </div>
    
    <!-- Edit Mode Controls - Now as sidebar -->
    <div v-if="editMode" class="edit-sidebar">
      <div class="edit-controls">
        <div class="selected-object-info">
          <h4>{{ selectedObject ? `Selected: ${selectedObject.userData.modelName}` : 'No object selected' }}</h4>
          <p v-if="!selectedObject">Click on a model to select it</p>
        </div>
        
        <div v-if="selectedObject" class="movement-controls">
          <div class="control-section">
            <h5>Position</h5>
            <div class="axis-control">
              <label>X Axis:</label>
              <div class="direction-buttons">
                <button @click="moveObject('x', -moveStep)" class="direction-btn">←</button>
                <button @click="moveObject('x', moveStep)" class="direction-btn">→</button>
              </div>
            </div>
            
            <div class="axis-control">
              <label>Y Axis:</label>
              <div class="direction-buttons">
                <button @click="moveObject('y', -moveStep)" class="direction-btn">↓</button>
                <button @click="moveObject('y', moveStep)" class="direction-btn">↑</button>
              </div>
            </div>
            
            <div class="axis-control">
              <label>Z Axis:</label>
              <div class="direction-buttons">
                <button @click="moveObject('z', moveStep)" class="direction-btn">←</button>
                <button @click="moveObject('z', -moveStep)" class="direction-btn">→</button>
              </div>
            </div>
          </div>
          
          <div class="control-section">
            <h5>Rotation</h5>
            <div class="axis-control">
              <label>X Axis:</label>
              <div class="direction-buttons">
                <button @click="rotateObject('x', -moveStep * 15)" class="direction-btn rotation-btn">↻</button>
                <button @click="rotateObject('x', moveStep * 15)" class="direction-btn rotation-btn">↺</button>
              </div>
            </div>
            
            <div class="axis-control">
              <label>Y Axis:</label>
              <div class="direction-buttons">
                <button @click="rotateObject('y', -moveStep * 15)" class="direction-btn rotation-btn">↻</button>
                <button @click="rotateObject('y', moveStep * 15)" class="direction-btn rotation-btn">↺</button>
              </div>
            </div>
            
            <div class="axis-control">
              <label>Z Axis:</label>
              <div class="direction-buttons">
                <button @click="rotateObject('z', -moveStep * 15)" class="direction-btn rotation-btn">↻</button>
                <button @click="rotateObject('z', moveStep * 15)" class="direction-btn rotation-btn">↺</button>
              </div>
            </div>
          </div>
          
          <div class="control-section">
            <h5>Scale</h5>
            <div class="axis-control">
              <label>Size:</label>
              <div class="scale-buttons">
                <button @click="scaleObject(-0.1)" class="direction-btn scale-btn">-</button>
                <span class="scale-display">{{ (selectedObject.scale?.x || 1).toFixed(1) }}</span>
                <button @click="scaleObject(0.1)" class="direction-btn scale-btn">+</button>
              </div>
            </div>
          </div>
          
          <div class="control-section">
            <h5>Material</h5>
            <div class="axis-control">
              <label>Color:</label>
              <input 
                type="color" 
                :value="selectedObjectMaterial.color" 
                @input="updateMaterialColor($event.target.value)"
                class="material-color-picker"
              />
            </div>
            
            <div class="axis-control">
              <label>Roughness:</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                :value="selectedObjectMaterial.roughness" 
                @input="updateMaterialProperty('roughness', parseFloat($event.target.value))"
                class="material-slider"
              />
              <span class="value-display">{{ selectedObjectMaterial.roughness.toFixed(1) }}</span>
            </div>
            
            <div class="axis-control">
              <label>Metalness:</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                :value="selectedObjectMaterial.metalness" 
                @input="updateMaterialProperty('metalness', parseFloat($event.target.value))"
                class="material-slider"
              />
              <span class="value-display">{{ selectedObjectMaterial.metalness.toFixed(1) }}</span>
            </div>
            
            <div class="axis-control">
              <label>Emission:</label>
              <input 
                type="color" 
                :value="selectedObjectMaterial.emissive" 
                @input="updateMaterialEmissive($event.target.value)"
                class="material-color-picker"
              />
            </div>
            
            <div class="axis-control">
              <label>Glow:</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                :value="selectedObjectMaterial.emissiveIntensity" 
                @input="updateMaterialProperty('emissiveIntensity', parseFloat($event.target.value))"
                class="material-slider"
              />
              <span class="value-display">{{ selectedObjectMaterial.emissiveIntensity.toFixed(1) }}</span>
            </div>
          </div>
          
          <div class="step-control">
            <label>Step Size:</label>
            <select v-model="moveStep">
              <option value="0.1">0.1</option>
              <option value="0.5">0.5</option>
              <option value="1">1.0</option>
              <option value="2">2.0</option>
            </select>
          </div>
          
          <div class="reset-controls">
            <button @click="resetObjectPosition" class="control-button reset-btn small">
              Reset Position
            </button>
            <button @click="resetObjectRotation" class="control-button reset-btn small">
              Reset Rotation
            </button>
            <button @click="resetObjectTransform" class="control-button reset-btn">
              Reset All
            </button>
          </div>
        </div>
      </div>
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
  emits: ['model-position-changed', 'model-rotation-changed', 'model-scale-changed', 'model-material-changed'],
  setup(props, { emit }) {
    const container = ref(null);
    const isLoading = ref(true);
    const showGrid = ref(true);
    const editMode = ref(false);
    const selectedObject = ref(null);
    const moveStep = ref(1);
    
    // Material properties for selected object
    const selectedObjectMaterial = ref({
      color: '#cccccc',
      roughness: 0.7,
      metalness: 0.1,
      emissive: '#000000',
      emissiveIntensity: 0.0
    });
    
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
    let animationFrameId = null;
    let raycaster, mouse;
    let highlightMaterial, originalMaterials = new Map();
    
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
        failIfMajorPerformanceCaveat: false,
        alpha: true
      });
      
      // Ensure minimum width for renderer
      const containerWidth = Math.max(container.value.clientWidth, 800);
      renderer.setSize(containerWidth, container.value.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      
      // Check if container already has a canvas and remove it
      const existingCanvas = container.value.querySelector('canvas');
      if (existingCanvas) {
        container.value.removeChild(existingCanvas);
      }
      
      container.value.appendChild(renderer.domElement);
      
      // Initialize raycaster and mouse for object selection
      raycaster = new THREE.Raycaster();
      mouse = new THREE.Vector2();
      
      // Create highlight material for selected objects
      highlightMaterial = new THREE.MeshStandardMaterial({
        color: 0xff6b00,
        transparent: true,
        opacity: 0.8,
        emissive: 0xff6b00,
        emissiveIntensity: 0.3
      });
      
      // Add click event listener for object selection
      renderer.domElement.addEventListener('click', onMouseClick, false);
      
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
    
    // Handle mouse click for object selection
    const onMouseClick = (event) => {
      if (!editMode.value) return;
      
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      raycaster.setFromCamera(mouse, camera);
      
      const selectableObjects = [];
      loadedModels.forEach(model => {
        model.traverse(child => {
          if (child.isMesh) {
            selectableObjects.push(child);
          }
        });
      });
      
      const intersects = raycaster.intersectObjects(selectableObjects);
      
      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        // Find the parent model object
        let parentModel = clickedObject;
        while (parentModel.parent && !loadedModels.has(parentModel.userData.modelId)) {
          parentModel = parentModel.parent;
        }
        
        selectObject(parentModel);
      } else {
        selectObject(null);
      }
    };
    
    // Select/deselect object
    const selectObject = (object) => {
      // Restore previous object's material
      if (selectedObject.value) {
        restoreObjectMaterial(selectedObject.value);
      }
      
      selectedObject.value = object;
      
      // Update material properties display
      if (selectedObject.value) {
        updateMaterialDisplay();
        highlightObject(selectedObject.value);
      }
    };
    
    // Update material display values
    const updateMaterialDisplay = () => {
      if (!selectedObject.value) return;
      
      // Find the first mesh to get material properties
      let meshMaterial = null;
      selectedObject.value.traverse(child => {
        if (child.isMesh && !meshMaterial) {
          meshMaterial = originalMaterials.get(child) || child.material;
        }
      });
      
      if (meshMaterial) {
        selectedObjectMaterial.value = {
          color: '#' + meshMaterial.color.getHexString(),
          roughness: meshMaterial.roughness || 0.7,
          metalness: meshMaterial.metalness || 0.1,
          emissive: '#' + meshMaterial.emissive.getHexString(),
          emissiveIntensity: meshMaterial.emissiveIntensity || 0.0
        };
      }
    };
    
    // Update material color
    const updateMaterialColor = (colorHex) => {
      if (!selectedObject.value) return;
      
      selectedObjectMaterial.value.color = colorHex;
      
      selectedObject.value.traverse(child => {
        if (child.isMesh) {
          const material = originalMaterials.get(child);
          if (material) {
            material.color.setHex(colorHex.replace('#', '0x'));
          }
        }
      });
      
      emitMaterialChange();
    };
    
    // Update material emissive color
    const updateMaterialEmissive = (colorHex) => {
      if (!selectedObject.value) return;
      
      selectedObjectMaterial.value.emissive = colorHex;
      
      selectedObject.value.traverse(child => {
        if (child.isMesh) {
          const material = originalMaterials.get(child);
          if (material) {
            material.emissive.setHex(colorHex.replace('#', '0x'));
          }
        }
      });
      
      emitMaterialChange();
    };
    
    // Update material property (roughness, metalness, emissiveIntensity)
    const updateMaterialProperty = (property, value) => {
      if (!selectedObject.value) return;
      
      selectedObjectMaterial.value[property] = value;
      
      selectedObject.value.traverse(child => {
        if (child.isMesh) {
          const material = originalMaterials.get(child);
          if (material && material[property] !== undefined) {
            material[property] = value;
          }
        }
      });
      
      emitMaterialChange();
    };
    
    // Emit material change event
    const emitMaterialChange = () => {
      if (!selectedObject.value) return;
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-material-changed', { 
        modelId, 
        material: { ...selectedObjectMaterial.value } 
      });
    };
    
    // Highlight selected object
    const highlightObject = (object) => {
      object.traverse(child => {
        if (child.isMesh) {
          if (!originalMaterials.has(child)) {
            originalMaterials.set(child, child.material);
          }
          child.material = highlightMaterial;
        }
      });
    };
    
    // Restore object's original material
    const restoreObjectMaterial = (object) => {
      object.traverse(child => {
        if (child.isMesh && originalMaterials.has(child)) {
          child.material = originalMaterials.get(child);
        }
      });
    };
    
    // Toggle edit mode
    const toggleEditMode = () => {
      editMode.value = !editMode.value;
      
      if (!editMode.value) {
        selectObject(null);
      }
      
      // Enable/disable orbit controls when in edit mode
      if (controls) {
        controls.enabled = !editMode.value;
      }
    };
    
    // Move selected object
    const moveObject = (axis, delta) => {
      if (!selectedObject.value) return;
      
      selectedObject.value.position[axis] += delta;
      
      // Emit position change event
      const modelId = selectedObject.value.userData.modelId;
      const newPosition = {
        x: selectedObject.value.position.x,
        y: selectedObject.value.position.y,
        z: selectedObject.value.position.z
      };
      
      emit('model-position-changed', { modelId, position: newPosition });
    };
    
    // Rotate selected object
    const rotateObject = (axis, delta) => {
      if (!selectedObject.value) return;
      
      // Convert delta from degrees to radians
      const radians = THREE.MathUtils.degToRad(delta);
      selectedObject.value.rotation[axis] += radians;
      
      // Emit rotation change event (convert back to degrees for consistency)
      const modelId = selectedObject.value.userData.modelId;
      const newRotation = {
        x: THREE.MathUtils.radToDeg(selectedObject.value.rotation.x),
        y: THREE.MathUtils.radToDeg(selectedObject.value.rotation.y),
        z: THREE.MathUtils.radToDeg(selectedObject.value.rotation.z)
      };
      
      emit('model-rotation-changed', { modelId, rotation: newRotation });
    };
    
    // Scale selected object
    const scaleObject = (delta) => {
      if (!selectedObject.value) return;
      
      const newScale = Math.max(0.1, (selectedObject.value.scale.x || 1) + delta);
      selectedObject.value.scale.set(newScale, newScale, newScale);
      
      // Emit scale change event
      const modelId = selectedObject.value.userData.modelId;
      emit('model-scale-changed', { modelId, scale: newScale });
    };
    
    // Reset selected object position
    const resetObjectPosition = () => {
      if (!selectedObject.value) return;
      
      selectedObject.value.position.set(0, 0, 0);
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-position-changed', { 
        modelId, 
        position: { x: 0, y: 0, z: 0 } 
      });
    };
    
    // Reset selected object rotation
    const resetObjectRotation = () => {
      if (!selectedObject.value) return;
      
      selectedObject.value.rotation.set(0, 0, 0);
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-rotation-changed', { 
        modelId, 
        rotation: { x: 0, y: 0, z: 0 } 
      });
    };
    
    // Reset selected object scale
    const resetObjectScale = () => {
      if (!selectedObject.value) return;
      
      selectedObject.value.scale.set(1, 1, 1);
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-scale-changed', { modelId, scale: 1 });
    };
    
    // Reset both position, rotation and scale
    const resetObjectTransform = () => {
      resetObjectPosition();
      resetObjectRotation();
      resetObjectScale();
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
        
        // Store model metadata
        object.userData.modelId = modelData.id;
        object.userData.modelName = modelData.name || `Model ${modelData.id}`;
        
        // Apply material/color if specified
        if (modelData.color || modelData.material) {
          const materialProps = {
            color: new THREE.Color(modelData.color || '#cccccc'),
            roughness: modelData.material?.roughness || 0.7,
            metalness: modelData.material?.metalness || 0.1,
            emissive: new THREE.Color(modelData.material?.emissive || '#000000'),
            emissiveIntensity: modelData.material?.emissiveIntensity || 0.0
          };
          
          const material = new THREE.MeshStandardMaterial(materialProps);
          
          object.traverse((child) => {
            if (child.isMesh) {
              child.material = material;
              child.castShadow = true;
              child.receiveShadow = true;
              // Store original material for highlighting
              originalMaterials.set(child, material);
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
    
    // Update existing model properties instead of reloading
    const updateModelProperties = (modelData) => {
      const existingModel = loadedModels.get(modelData.id);
      if (!existingModel) return;
      
      // Update position
      if (modelData.position) {
        existingModel.position.set(
          modelData.position.x || 0,
          modelData.position.y || 0,
          modelData.position.z || 0
        );
      }
      
      // Update rotation
      if (modelData.rotation) {
        existingModel.rotation.set(
          THREE.MathUtils.degToRad(modelData.rotation.x || 0),
          THREE.MathUtils.degToRad(modelData.rotation.y || 0),
          THREE.MathUtils.degToRad(modelData.rotation.z || 0)
        );
      }
      
      // Update scale
      if (modelData.scale) {
        const scale = typeof modelData.scale === 'number' 
          ? modelData.scale 
          : modelData.scale.x || 1;
        existingModel.scale.set(scale, scale, scale);
      }
      
      // Update material properties
      if (modelData.color || modelData.material) {
        const materialProps = {
          color: new THREE.Color(modelData.color || '#cccccc'),
          roughness: modelData.material?.roughness || 0.7,
          metalness: modelData.material?.metalness || 0.1,
          emissive: new THREE.Color(modelData.material?.emissive || '#000000'),
          emissiveIntensity: modelData.material?.emissiveIntensity || 0.0
        };
        
        existingModel.traverse((child) => {
          if (child.isMesh) {
            const material = originalMaterials.get(child);
            if (material) {
              material.color.copy(materialProps.color);
              material.roughness = materialProps.roughness;
              material.metalness = materialProps.metalness;
              material.emissive.copy(materialProps.emissive);
              material.emissiveIntensity = materialProps.emissiveIntensity;
            }
          }
        });
      }
    };

    // Smart model management - only add/remove/update as needed
    const manageModels = async () => {
      if (!modelsToLoad.value || modelsToLoad.value.length === 0) {
        // Remove all models if none to load
        loadedModels.forEach((model, modelId) => {
          scene.remove(model);
          loadedModels.delete(modelId);
        });
        return;
      }
      
      const currentModelIds = new Set(Array.from(loadedModels.keys()));
      const newModelIds = new Set(modelsToLoad.value.map(m => m.id));
      
      // Remove models that are no longer in the list
      for (const modelId of currentModelIds) {
        if (!newModelIds.has(modelId)) {
          const model = loadedModels.get(modelId);
          scene.remove(model);
          loadedModels.delete(modelId);
        }
      }
      
      // Add new models or update existing ones
      for (const modelData of modelsToLoad.value) {
        if (loadedModels.has(modelData.id)) {
          // Update existing model properties
          updateModelProperties(modelData);
        } else {
          // Load new model
          await loadModel(modelData);
        }
      }
      
      // Only adjust camera if we have models and it's the first load
      if (loadedModels.size > 0 && currentModelIds.size === 0) {
        setTimeout(() => {
          fitCameraToModels();
        }, 100);
      }
    };

    // Load all models
    const loadModels = async () => {
      isLoading.value = true;
      
      try {
        await manageModels();
      } catch (err) {
        console.error('Error managing models:', err);
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
      
      // Remove event listeners
      if (renderer && renderer.domElement) {
        renderer.domElement.removeEventListener('click', onMouseClick);
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
      
      // Clear material maps
      originalMaterials.clear();
      
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
    
    // Handle window resize - updated for more responsive behavior
    const handleResize = () => {
      if (camera && renderer && container.value) {
        // Force a minimum width for the container
        const containerWidth = Math.max(container.value.clientWidth, 800);
        const containerHeight = container.value.clientHeight;
        
        camera.aspect = containerWidth / containerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(containerWidth, containerHeight);
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
    
    // Watch for changes to models array with smart updating
    watch([() => props.models], async () => {
      console.log('Models prop changed, managing models intelligently');
      await manageModels();
    }, { deep: true });
    
    return {
      container,
      isLoading,
      showGrid,
      editMode,
      selectedObject,
      moveStep,
      selectedObjectMaterial,
      resetCamera,
      toggleGrid,
      toggleEditMode,
      moveObject,
      rotateObject,
      resetObjectPosition,
      resetObjectRotation,
      resetObjectTransform,
      scaleObject,
      updateMaterialColor,
      updateMaterialEmissive,
      updateMaterialProperty
    };
  }
};
</script>

<style scoped>
.model-viewer-wrapper {
  display: flex;
  width: 100%;
  height: 100%;
}

.model-viewer-container {
  position: relative;
  flex: 1;
  height: 100%;
  min-width: 700px;
  min-height: 500px;
  border-right: 1px solid #ddd;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

#modelViewer {
  width: 100%;
  height: 100%;
  min-width: 900px;
  min-height: 500px;
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

.control-button.active {
  background-color: #ff6b00;
}

.edit-sidebar {
  width: 320px;
  height: 100%;
  background-color: #f8f9fa;
  border-left: 1px solid #ddd;
  overflow-y: auto;
  flex-shrink: 0;
}

.edit-controls {
  padding: 15px;
  height: 100%;
}

.selected-object-info {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.selected-object-info h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 14px;
}

.selected-object-info p {
  margin: 0;
  color: #666;
  font-size: 12px;
}

.movement-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.control-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.control-section h5 {
  margin: 0 0 6px 0;
  color: #333;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.axis-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.axis-control label {
  font-weight: bold;
  color: #333;
  font-size: 11px;
  min-width: 35px;
}

.direction-buttons {
  display: flex;
  gap: 3px;
}

.direction-btn {
  width: 28px;
  height: 28px;
  border: 1px solid #ddd;
  background-color: white;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s;
}

.direction-btn:hover {
  background-color: #f0f0f0;
  border-color: #2196f3;
}

.direction-btn:active {
  background-color: #2196f3;
  color: white;
}

.rotation-btn {
  background-color: #f8f9fa;
  border-color: #e3f2fd;
  color: #1976d2;
}

.rotation-btn:hover {
  background-color: #e3f2fd;
  border-color: #1976d2;
}

.rotation-btn:active {
  background-color: #1976d2;
  color: white;
}

.step-control {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 10px 0;
}

.step-control label {
  font-weight: bold;
  color: #333;
  font-size: 11px;
}

.step-control select {
  padding: 3px 6px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 11px;
}

.reset-controls {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 12px;
}

.reset-controls .small {
  font-size: 10px;
  padding: 3px 6px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 3px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reset-controls .small:hover {
  background-color: #e0e0e0;
}

.reset-btn {
  background-color: #f44336 !important;
  font-size: 12px;
  padding: 6px 12px;
}

.reset-btn:hover {
  background-color: #d32f2f !important;
}

.scale-buttons {
  display: flex;
  align-items: center;
  gap: 6px;
}

.scale-display {
  min-width: 35px;
  text-align: center;
  font-weight: bold;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 3px 6px;
  font-size: 11px;
}

.scale-btn {
  width: 28px;
  height: 28px;
  background-color: #e8f5e8;
  border-color: #4caf50;
  color: #2e7d32;
  font-weight: bold;
}

.scale-btn:hover {
  background-color: #c8e6c9;
  border-color: #2e7d32;
}

.scale-btn:active {
  background-color: #4caf50;
  color: white;
}

.material-color-picker {
  width: 40px;
  height: 30px;
  border: 1px solid #ddd;
  border-radius: 3px;
  cursor: pointer;
  padding: 0;
}

.material-slider {
  flex: 1;
  margin: 0 8px;
}

.value-display {
  min-width: 30px;
  text-align: center;
  font-size: 11px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 2px 4px;
}
</style>
