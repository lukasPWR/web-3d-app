<template>
  <div class="model-viewer-wrapper">
    <div class="model-viewer-container">
      <div id="modelViewer" ref="container"></div>
      <div v-if="isLoading" class="loading-overlay">
        <p>Loading models...</p>
      </div>
      
      <!-- FIXED: Scene controls should always be visible -->
      <div class="scene-controls">
        <button @click="resetCamera" class="control-button">Reset View</button>
        <button @click="toggleGrid" class="control-button">{{ showGrid ? 'Hide' : 'Show' }} Grid</button>
        <button @click="toggleEditMode" class="control-button" :class="{ 'active': editMode }">
          {{ editMode ? 'Exit Edit' : 'Edit Mode' }}
        </button>
        <!-- NEW: Vertex visualization toggle -->
        <button @click="toggleVertexVisualization" class="control-button" :class="{ 'active': showVertices }">
          {{ showVertices ? 'Hide' : 'Show' }} Vertices
        </button>
        <button @click="toggleWireframe" class="control-button" :class="{ 'active': showWireframe }">
          {{ showWireframe ? 'Hide' : 'Show' }} Wireframe
        </button>
      </div>
      
      <!-- Mouse Controls Info -->
      <div v-if="editMode" class="mouse-controls-info">
        <div class="controls-help">
          <h5>Mouse Controls:</h5>
          <ul>
            <li><strong>Drag:</strong> Move object in screen plane</li>
            <li><strong>Shift + Drag:</strong> Rotate object</li>
            <li><strong>Ctrl + Drag:</strong> Move along Z-axis</li>
            <li><strong>Scroll:</strong> Scale object</li>
          </ul>
        </div>
      </div>

      <!-- Vertex Visualization Controls -->
      <div v-if="showVertices" class="vertex-controls">
        <div class="vertex-settings">
          <h5>Vertex Visualization</h5>
          <div class="control-row">
            <label>Size:</label>
            <input 
              type="range" 
              min="0.01" 
              max="0.5" 
              step="0.01"
              v-model="vertexSettings.size"
              @input="updateVertexVisualization"
              class="vertex-slider"
            />
            <span>{{ vertexSettings.size }}</span>
          </div>
          <div class="control-row">
            <label>Color:</label>
            <input 
              type="color" 
              v-model="vertexSettings.color"
              @input="updateVertexVisualization"
              class="vertex-color-picker"
            />
          </div>
          <div class="control-row">
            <label>Opacity:</label>
            <input 
              type="range" 
              min="0.1" 
              max="1" 
              step="0.1"
              v-model="vertexSettings.opacity"
              @input="updateVertexVisualization"
              class="vertex-slider"
            />
            <span>{{ vertexSettings.opacity }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Edit Mode Controls - Now as sidebar -->
    <div v-if="editMode" class="edit-sidebar">
      <div class="edit-controls">
        <!-- Selected object info -->
        <div v-if="selectedObject" class="selected-object-info">
          <h4>Selected Model</h4>
          <p>{{ selectedObject.userData.modelName || 'Unnamed Model' }}</p>
        </div>

        <div v-if="selectedObject" class="movement-controls">
          <div class="control-section">
            <h5>Position</h5>
            <div class="control-hint">
              <span>💡 Drag object directly or use buttons below</span>
            </div>
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
            <div class="control-hint">
              <span>💡 Hold Shift + Drag for rotation or use buttons below</span>
            </div>
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
            <div class="control-hint">
              <span>💡 Use mouse wheel or buttons below</span>
            </div>
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
                @input="updateMaterialRoughness($event.target.value)"
                class="material-slider"
              />
              <span>{{ selectedObjectMaterial.roughness }}</span>
            </div>
            
            <div class="axis-control">
              <label>Metalness:</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1"
                :value="selectedObjectMaterial.metalness" 
                @input="updateMaterialMetalness($event.target.value)"
                class="material-slider"
              />
              <span>{{ selectedObjectMaterial.metalness }}</span>
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
            
            <!-- NEW: Texture Selection -->
            <div class="axis-control">
              <label>Texture:</label>
              <select 
                v-model="selectedObjectMaterial.textureId" 
                @change="applySelectedTexture($event.target.value)"
                class="texture-selector"
              >
                <option value="">No Texture</option>
                <option v-for="texture in availableTextures" :key="texture.id" :value="texture.id">
                  {{ texture.name }}
                </option>
              </select>
            </div>

            <!-- Texture Upload -->
            <div class="axis-control">
              <label>Upload:</label>
              <input 
                type="file" 
                ref="textureFileInput"
                @change="handleTextureUpload"
                accept=".jpg,.jpeg,.png,.bmp,.tga,.tiff"
                class="texture-upload-input"
              />
            </div>
            
            <!-- Show texture preview if texture is selected -->
            <div v-if="selectedObjectMaterial.textureId" class="texture-preview">
              <img 
                :src="getSelectedTextureUrl()" 
                :alt="getSelectedTextureName()"
                class="texture-preview-image"
                @error="onTexturePreviewError"
              />
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
        
        <!-- Update Model button - NEW SECTION -->
        <div class="control-section">
          <h5>Save Changes</h5>
          <div class="update-controls">
            <button 
              @click="updateModelChanges" 
              class="update-btn" 
              :disabled="isUpdating">
              {{ isUpdating ? 'Updating...' : 'Update Model with Changes' }}
            </button>
            
            <div v-if="updateStatus.show" :class="['update-status', updateStatus.type]">
              {{ updateStatus.message }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- FIXED: Model Analyzer should be shown when NOT in edit mode -->
    <ModelAnalyzer v-if="!editMode" />
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount, watch, computed, provide } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { MTLLoader } from 'three/examples/jsm/loaders/MTLLoader.js';
import axios from 'axios'; // Make sure axios is imported
import api from '../services/api.js';
import ModelAnalyzer from './ModelAnalyzer.vue';

export default {
  name: 'SimpleModelViewer',
  components: {
    ModelAnalyzer
  },
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
  emits: ['model-position-changed', 'model-rotation-changed', 'model-scale-changed', 'model-material-changed', 'model-updated'],
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
      emissiveIntensity: 0.0,
      textureId: '',
      textureScale: 1
    });
    
    // Available textures from backend
    const availableTextures = ref([]);
    const textureFileInput = ref(null);
    
    // Texture cache
    const textureLoader = new THREE.TextureLoader();
    const loadedTextures = new Map();
    
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
    
    // Mouse control state
    let isDragging = false;
    let dragStartMouse = new THREE.Vector2();
    let dragStartPosition = new THREE.Vector3();
    let dragStartRotation = new THREE.Vector3();
    let dragPlane = new THREE.Plane();
    let dragPlaneHelper = new THREE.PlaneHelper(dragPlane, 10, 0x00ff00);
    dragPlaneHelper.visible = false;
    
    // Map to track loaded models - key: modelId, value: THREE.Object3D
    const loadedModels = reactive(new Map());
    
    // NEW: Vertex visualization state
    const showVertices = ref(false);
    const showWireframe = ref(false);
    const vertexSettings = reactive({
      size: 0.05,
      color: '#ff0000',
      opacity: 0.8
    });
    
    // Store vertex point clouds for each model
    const vertexPointClouds = new Map();
    const wireframeObjects = new Map();
    
    // NEW: Add missing reactive variables
    const isUpdating = ref(false);
    const updateStatus = reactive({
      show: false,
      message: '',
      type: 'info' // 'success', 'error', 'warning', 'info'
    });
    
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
      renderer.domElement.addEventListener('mousedown', onMouseDown, false);
      renderer.domElement.addEventListener('mousemove', onMouseMove, false);
      renderer.domElement.addEventListener('mouseup', onMouseUp, false);
      renderer.domElement.addEventListener('wheel', onMouseWheel, false);
      renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault(), false);
      
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
      if (!editMode.value || isDragging) return;
      
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
    
    // Handle mouse down for dragging
    const onMouseDown = (event) => {
      if (!editMode.value || !selectedObject.value) return;
      
      event.preventDefault();
      
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      raycaster.setFromCamera(mouse, camera);
      
      // Check if we're clicking on the selected object
      const selectableObjects = [];
      selectedObject.value.traverse(child => {
        if (child.isMesh) {
          selectableObjects.push(child);
        }
      });
      
      const intersects = raycaster.intersectObjects(selectableObjects);
      
      if (intersects.length > 0) {
        isDragging = true;
        dragStartMouse.copy(mouse);
        dragStartPosition.copy(selectedObject.value.position);
        dragStartRotation.copy(selectedObject.value.rotation);
        
        // Create drag plane based on camera orientation
        const cameraDirection = new THREE.Vector3();
        camera.getWorldDirection(cameraDirection);
        
        // Use the object's position as the plane point
        const objectPosition = selectedObject.value.position.clone();
        
        // Create plane perpendicular to camera
        dragPlane.setFromNormalAndCoplanarPoint(cameraDirection, objectPosition);
        
        // Disable orbit controls while dragging
        if (controls) {
          controls.enabled = false;
        }
        
        // Change cursor
        renderer.domElement.style.cursor = event.shiftKey ? 'grab' : 'move';
      }
    };
    
    // Handle mouse move for dragging
    const onMouseMove = (event) => {
      if (!editMode.value || !isDragging || !selectedObject.value) return;
      
      event.preventDefault();
      
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      
      const mouseDelta = new THREE.Vector2().subVectors(mouse, dragStartMouse);
      
      if (event.shiftKey) {
        // Rotation mode with Shift key
        const rotationSpeed = 2;
        const deltaRotationX = mouseDelta.y * rotationSpeed;
        const deltaRotationY = mouseDelta.x * rotationSpeed;
        
        selectedObject.value.rotation.x = dragStartRotation.x + deltaRotationX;
        selectedObject.value.rotation.y = dragStartRotation.y + deltaRotationY;
        
        // Emit rotation change
        const modelId = selectedObject.value.userData.modelId;
        const newRotation = {
          x: THREE.MathUtils.radToDeg(selectedObject.value.rotation.x),
          y: THREE.MathUtils.radToDeg(selectedObject.value.rotation.y),
          z: THREE.MathUtils.radToDeg(selectedObject.value.rotation.z)
        };
        emit('model-rotation-changed', { modelId, rotation: newRotation });
        
      } else if (event.ctrlKey || event.metaKey) {
        // Z-axis movement with Ctrl/Cmd key
        const moveSpeed = 5;
        const deltaZ = mouseDelta.y * moveSpeed;
        
        selectedObject.value.position.z = dragStartPosition.z - deltaZ;
        
        // Emit position change
        const modelId = selectedObject.value.userData.modelId;
        const newPosition = {
          x: selectedObject.value.position.x,
          y: selectedObject.value.position.y,
          z: selectedObject.value.position.z
        };
        emit('model-position-changed', { modelId, position: newPosition });
        
      } else {
        // Normal dragging in screen space
        raycaster.setFromCamera(mouse, camera);
        
        const intersection = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(dragPlane, intersection)) {
          const dragPlaneStart = new THREE.Vector3();
          const startRaycaster = new THREE.Raycaster();
          startRaycaster.setFromCamera(dragStartMouse, camera);
          
          if (startRaycaster.ray.intersectPlane(dragPlane, dragPlaneStart)) {
            const movement = intersection.sub(dragPlaneStart);
            selectedObject.value.position.copy(dragStartPosition).add(movement);
            
            // Emit position change
            const modelId = selectedObject.value.userData.modelId;
            const newPosition = {
              x: selectedObject.value.position.x,
              y: selectedObject.value.position.y,
              z: selectedObject.value.position.z
            };
            emit('model-position-changed', { modelId, position: newPosition });
          }
        }
      }
    };
    
    // Handle mouse up
    const onMouseUp = (event) => {
      if (isDragging) {
        isDragging = false;
        
        // Re-enable orbit controls
        if (controls) {
          controls.enabled = true;
        }
        
        // Reset cursor
        renderer.domElement.style.cursor = 'default';
      }
    };
    
    // Handle mouse wheel for scaling
    const onMouseWheel = (event) => {
      if (!editMode.value || !selectedObject.value) return;
      
      event.preventDefault();
      
      const scaleSpeed = 0.1;
      const delta = event.deltaY > 0 ? -scaleSpeed : scaleSpeed;
      
      const currentScale = selectedObject.value.scale.x;
      const newScale = Math.max(0.1, currentScale + delta);
      
      selectedObject.value.scale.set(newScale, newScale, newScale);
      
      // Emit scale change
      const modelId = selectedObject.value.userData.modelId;
      emit('model-scale-changed', { modelId, scale: newScale });
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
    
    // Load textures from backend
    const loadTextures = async () => {
      try {
        const response = await api.getTextures();
        availableTextures.value = response.data;
      } catch (error) {
        console.error('Failed to load textures:', error);
      }
    };

    // Handle texture file upload
    const handleTextureUpload = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', file.name);
      formData.append('description', `Uploaded texture: ${file.name}`);
      formData.append('type', 'diffuse');
      formData.append('category', 'uploaded');

      try {
        const response = await api.uploadTexture(formData);
        const newTexture = response.data;
        
        // Add to available textures
        availableTextures.value.push(newTexture);
        
        // Automatically apply the uploaded texture
        selectedObjectMaterial.value.textureId = newTexture.id;
        await applySelectedTexture(newTexture.id);
        
        // Clear file input
        if (textureFileInput.value) {
          textureFileInput.value.value = '';
        }
        
        console.log('Texture uploaded successfully:', newTexture);
      } catch (error) {
        console.error('Failed to upload texture:', error);
        alert('Failed to upload texture. Please try again.');
      }
    };

    // Get selected texture URL
    const getSelectedTextureUrl = () => {
      if (!selectedObjectMaterial.value.textureId) return '';
      
      const texture = availableTextures.value.find(t => t.id === selectedObjectMaterial.value.textureId);
      return texture ? texture.textureUrl : '';
    };

    // Get selected texture name
    const getSelectedTextureName = () => {
      if (!selectedObjectMaterial.value.textureId) return '';
      
      const texture = availableTextures.value.find(t => t.id === selectedObjectMaterial.value.textureId);
      return texture ? texture.name : '';
    };

    // Load texture with caching
    const loadTexture = async (textureUrl) => {
      if (loadedTextures.has(textureUrl)) {
        return loadedTextures.get(textureUrl);
      }
      
      try {
        const texture = await new Promise((resolve, reject) => {
          textureLoader.load(
            textureUrl,
            (tex) => {
              tex.wrapS = THREE.RepeatWrapping;
              tex.wrapT = THREE.RepeatWrapping;
              tex.flipY = false;
              resolve(tex);
            },
            undefined,
            reject
          );
        });
        
        loadedTextures.set(textureUrl, texture);
        return texture;
      } catch (error) {
        console.warn(`Failed to load texture: ${textureUrl}`, error);
        return null;
      }
    };

    // Apply selected texture to object
    const applySelectedTexture = async (textureId) => {
      if (!selectedObject.value) return;
      
      selectedObjectMaterial.value.textureId = textureId;
      
      if (!textureId) {
        // Remove texture - use basic material
        await updateObjectMaterial();
        emitMaterialChange();
        return;
      }
      
      const texture = availableTextures.value.find(t => t.id === textureId);
      if (!texture) return;
      
      try {
        // Load the texture
        const loadedTexture = await loadTexture(texture.textureUrl);
        
        if (loadedTexture) {
          // Apply texture to material
          const textures = { map: loadedTexture };
          await updateObjectMaterial(textures);
          emitMaterialChange();
        }
      } catch (error) {
        console.error('Error applying texture:', error);
      }
    };

    // Handle texture preview error
    const onTexturePreviewError = (event) => {
      console.warn('Texture preview failed to load:', event.target.src);
      event.target.style.display = 'none';
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
          emissiveIntensity: meshMaterial.emissiveIntensity || 0.0,
          textureId: selectedObjectMaterial.value.textureId || '',
          textureScale: selectedObjectMaterial.value.textureScale || 1
        };
      }
    };
    
    // Update object material with optional textures
    const updateObjectMaterial = async (textures = {}) => {
      if (!selectedObject.value) return;
      
      selectedObject.value.traverse(child => {
        if (child.isMesh) {
          let material = originalMaterials.get(child);
          
          if (!material || Object.keys(textures).length > 0) {
            // Create new material with textures
            material = new THREE.MeshStandardMaterial({
              color: new THREE.Color(selectedObjectMaterial.value.color),
              roughness: selectedObjectMaterial.value.roughness,
              metalness: selectedObjectMaterial.value.metalness,
              emissive: new THREE.Color(selectedObjectMaterial.value.emissive),
              emissiveIntensity: selectedObjectMaterial.value.emissiveIntensity,
              ...textures
            });
            
            // Set texture scale
            const scale = selectedObjectMaterial.value.textureScale || 1;
            Object.values(textures).forEach(texture => {
              if (texture) {
                texture.repeat.set(scale, scale);
              }
            });
            
            originalMaterials.set(child, material);
            child.material = material;
          }
        }
      });
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
    
    // Load a model with MTL support (unified function)
    const loadModel = async (modelData) => {
      const modelPath = modelData.modelPath || modelData.modelUrl;
      
      if (!modelData || !modelData.id || (!modelData.modelPath && !modelData.modelUrl)) {
        console.error('Invalid model data provided:', modelData);
        return null;
      }
      
      // If we already loaded this model, remove it first
      if (loadedModels.has(modelData.id)) {
        const existingModel = loadedModels.get(modelData.id);
        scene.remove(existingModel);
        
        // Remove vertex visualization
        if (vertexPointClouds.has(modelData.id)) {
          scene.remove(vertexPointClouds.get(modelData.id));
          vertexPointClouds.delete(modelData.id);
        }
        
        // Remove wireframe visualization
        if (wireframeObjects.has(modelData.id)) {
          scene.remove(wireframeObjects.get(modelData.id));
          wireframeObjects.delete(modelData.id);
        }
        
        loadedModels.delete(modelData.id);
      }
      
      try {
        // FIXED: Proper MTL path handling to avoid double "models/" prefix
        let mtlPath = modelPath.replace('.obj', '.mtl');
        let materials = null;
        
        try {
          // Try to load MTL file
          const mtlLoader = new MTLLoader();
          
          // FIXED: Set the correct base path without duplicating 'models/'
          // Extract just the filename from the full path
          const filename = modelPath.split('/').pop();
          const mtlFilename = filename.replace('.obj', '.mtl');
          
          // Set the base path to the root directory where models are served
          mtlLoader.setPath('/');
          
          console.log(`Attempting to load MTL: /models/${mtlFilename}`);
          
          materials = await new Promise((resolve, reject) => {
            mtlLoader.load(
              `models/${mtlFilename}`, // FIXED: Correct path without double prefix
              (mtl) => {
                console.log(`Successfully loaded MTL file: /models/${mtlFilename}`);
                mtl.preload();
                resolve(mtl);
              },
              (xhr) => {
                console.log(`MTL loading progress: ${(xhr.loaded / xhr.total) * 100}%`);
              },
              (error) => {
                console.warn(`Failed to load MTL file: /models/${mtlFilename}`, error);
                resolve(null); // Don't reject, just continue without MTL
              }
            );
          });
        } catch (mtlError) {
          console.warn(`MTL loading error for ${modelData.id}:`, mtlError);
          materials = null;
        }
        
        // Load OBJ file
        const objLoader = new OBJLoader();
        
        // Apply materials if MTL was loaded successfully
        if (materials) {
          objLoader.setMaterials(materials);
          console.log(`Applied MTL materials to OBJ loader for ${modelData.id}`);
        }
        
        const object = await new Promise((resolve, reject) => {
          objLoader.load(
            modelPath,
            (obj) => {
              console.log(`Successfully loaded OBJ: ${modelPath}`);
              resolve(obj);
            },
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
        object.userData.hasMTL = !!materials;
        
        // Log material information for debugging
        let materialCount = 0;
        object.traverse((child) => {
          if (child.isMesh) {
            materialCount++;
            console.log(`Mesh material for ${modelData.id}:`, {
              materialName: child.material.name,
              color: child.material.color,
              hasMap: !!child.material.map,
              materialType: child.material.type
            });
            
            // Enable shadows
            child.castShadow = true;
            child.receiveShadow = true;
            
            // Store original material for highlighting
            originalMaterials.set(child, child.material);
          }
        });
        
        console.log(`Model ${modelData.id} loaded with ${materialCount} materials, MTL: ${!!materials}`);
        
        // Apply custom color/material ONLY if no MTL was loaded and custom properties are specified
        if (!materials && (modelData.color || modelData.material)) {
          console.log(`Applying custom material to ${modelData.id} (no MTL found)`);
          
          const materialProps = {
            color: new THREE.Color(modelData.color || '#cccccc'),
            roughness: modelData.material?.roughness || 0.7,
            metalness: modelData.material?.metalness || 0.1,
            emissive: new THREE.Color(modelData.material?.emissive || '#000000'),
            emissiveIntensity: modelData.material?.emissiveIntensity || 0.0
          };
          
          const customMaterial = new THREE.MeshStandardMaterial(materialProps);
          
          object.traverse((child) => {
            if (child.isMesh) {
              child.material = customMaterial;
              originalMaterials.set(child, customMaterial);
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
        
        // Add vertex visualization if enabled
        if (showVertices.value) {
          createModelVertexVisualization(object, modelData.id);
        }
        
        // Add wireframe if enabled
        if (showWireframe.value) {
          createModelWireframeVisualization(object, modelData.id);
        }
        
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
          
          // Remove vertex visualization
          if (vertexPointClouds.has(modelId)) {
            scene.remove(vertexPointClouds.get(modelId));
            vertexPointClouds.delete(modelId);
          }
          
          // Remove wireframe visualization  
          if (wireframeObjects.has(modelId)) {
            scene.remove(wireframeObjects.get(modelId));
            wireframeObjects.delete(modelId);
          }
          
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
          
          // Remove vertex visualization
          if (vertexPointClouds.has(modelId)) {
            scene.remove(vertexPointClouds.get(modelId));
            vertexPointClouds.delete(modelId);
          }
          
          // Remove wireframe visualization
          if (wireframeObjects.has(modelId)) {
            scene.remove(wireframeObjects.get(modelId));
            wireframeObjects.delete(modelId);
          }
          
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
      
      // FIXED: Always fit camera when models change, with a proper delay
      if (loadedModels.size > 0) {
        setTimeout(() => {
          fitCameraToModels();
        }, 200); // Increased delay to ensure all models are properly loaded and positioned
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
      
      // FIXED: Improved camera distance calculation
      const maxDim = Math.max(size.x, size.y, size.z);
      
      // Ensure minimum size for very small models
      const effectiveSize = Math.max(maxDim, 2);
      
      const fov = camera.fov * (Math.PI / 180);
      let distance = effectiveSize / (2 * Math.tan(fov / 2));
      
      // FIXED: Better padding calculation based on model count and size
      const modelCount = loadedModels.size;
      const paddingMultiplier = Math.max(2.5, 1.5 + (modelCount * 0.3));
      distance *= paddingMultiplier;
      
      // FIXED: Ensure minimum distance for proper viewing
      distance = Math.max(distance, effectiveSize * 3);
      
      // FIXED: Better camera positioning - position camera at an angle for better view
      const cameraOffset = new THREE.Vector3(
        distance * 0.7, // X offset
        distance * 0.5, // Y offset (height)
        distance * 0.7  // Z offset
      );
      
      camera.position.copy(center).add(cameraOffset);
      controls.target.copy(center);
      
      // FIXED: Update camera near/far planes based on scene size
      camera.near = Math.max(0.1, distance / 1000);
      camera.far = distance * 10;
      camera.updateProjectionMatrix();
      
      controls.update();
      
      console.log(`Camera fitted to ${modelCount} models:`, {
        boundingBoxSize: size,
        effectiveSize,
        distance,
        cameraPosition: camera.position,
        targetPosition: controls.target
      });
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
        renderer.domElement.removeEventListener('mousedown', onMouseDown);
        renderer.domElement.removeEventListener('mousemove', onMouseMove);
        renderer.domElement.removeEventListener('mouseup', onMouseUp);
        renderer.domElement.removeEventListener('wheel', onMouseWheel);
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
          loadTextures(); // Load available textures
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
    
    // Provide loaded models to child components
    provide('threeScene', {
      loadedModels
    });
    
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
    
    // Add missing material update functions
    const updateMaterialRoughness = (value) => {
      updateMaterialProperty('roughness', parseFloat(value));
    };
    
    const updateMaterialMetalness = (value) => {
      updateMaterialProperty('metalness', parseFloat(value));
    };
    
    // Highlight selected object
    const highlightObject = (object) => {
      object.traverse(child => {
        if (child.isMesh) {
          if (!originalMaterials.has(child)) {
            originalMaterials.set(child, child.material);
          }
          child.material = highlightMaterial;
          child.userData.draggable = true;
        }
      });
    };
    
    // Restore object's original material
    const restoreObjectMaterial = (object) => {
      object.traverse(child => {
        if (child.isMesh && originalMaterials.has(child)) {
          child.material = originalMaterials.get(child);
          child.userData.draggable = false;
        }
      });
    };
    
    // Toggle edit mode
    const toggleEditMode = () => {
      editMode.value = !editMode.value;
      
      if (!editMode.value) {
        selectObject(null);
        isDragging = false;
        renderer.domElement.style.cursor = 'default';
      }
      
      if (controls) {
        controls.enabled = !editMode.value;
      }
    };
    
    // Move selected object
    const moveObject = (axis, delta) => {
      if (!selectedObject.value) return;
      
      selectedObject.value.position[axis] += delta;
      
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
      
      const radians = THREE.MathUtils.degToRad(delta);
      selectedObject.value.rotation[axis] += radians;
      
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
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-scale-changed', { modelId, scale: newScale });
    };

    // NEW: Toggle vertex visualization
    const toggleVertexVisualization = () => {
      showVertices.value = !showVertices.value;
      
      if (showVertices.value) {
        createVertexVisualization();
      } else {
        removeVertexVisualization();
      }
    };
    
    // NEW: Toggle wireframe
    const toggleWireframe = () => {
      showWireframe.value = !showWireframe.value;
      
      if (showWireframe.value) {
        createWireframeVisualization();
      } else {
        removeWireframeVisualization();
      }
    };
    
    // NEW: Create vertex visualization for all loaded models
    const createVertexVisualization = () => {
      loadedModels.forEach((model, modelId) => {
        createModelVertexVisualization(model, modelId);
      });
    };
    
    // NEW: Create vertex visualization for a specific model
    const createModelVertexVisualization = (model, modelId) => {
      // Remove existing vertex visualization for this model
      if (vertexPointClouds.has(modelId)) {
        scene.remove(vertexPointClouds.get(modelId));
        vertexPointClouds.delete(modelId);
      }
      
      const allVertices = [];
      
      // Collect all vertices from all meshes in the model
      model.traverse((child) => {
        if (child.isMesh && child.geometry) {
          const geometry = child.geometry;
          const positions = geometry.attributes.position;
          
          if (positions) {
            // Transform vertices to world coordinates
            child.updateMatrixWorld(true);
            
            for (let i = 0; i < positions.count; i++) {
              const vertex = new THREE.Vector3(
                positions.getX(i),
                positions.getY(i),
                positions.getZ(i)
              );
              
              // Transform to world coordinates
              vertex.applyMatrix4(child.matrixWorld);
              allVertices.push(vertex.x, vertex.y, vertex.z);
            }
          }
        }
      });
      
      if (allVertices.length > 0) {
        // Create point cloud geometry
        const pointGeometry = new THREE.BufferGeometry();
        pointGeometry.setAttribute('position', new THREE.Float32BufferAttribute(allVertices, 3));
        
        // Create point material
        const pointMaterial = new THREE.PointsMaterial({
          color: new THREE.Color(vertexSettings.color),
          size: vertexSettings.size,
          transparent: true,
          opacity: vertexSettings.opacity,
          sizeAttenuation: true
        });
        
        // Create point cloud
        const pointCloud = new THREE.Points(pointGeometry, pointMaterial);
        pointCloud.userData.modelId = modelId;
        pointCloud.userData.isVertexVisualization = true;
        
        scene.add(pointCloud);
        vertexPointClouds.set(modelId, pointCloud);
      }
    };
    
    // NEW: Create wireframe visualization
    const createWireframeVisualization = () => {
      loadedModels.forEach((model, modelId) => {
        createModelWireframeVisualization(model, modelId);
      });
    };
    
    // NEW: Create wireframe for a specific model
    const createModelWireframeVisualization = (model, modelId) => {
      // Remove existing wireframe for this model
      if (wireframeObjects.has(modelId)) {
        scene.remove(wireframeObjects.get(modelId));
        wireframeObjects.delete(modelId);
      }
      
      const wireframeGroup = new THREE.Group();
      
      model.traverse((child) => {
        if (child.isMesh && child.geometry) {
          // Create wireframe geometry
          const wireframeGeometry = new THREE.WireframeGeometry(child.geometry);
          
          // Create wireframe material
          const wireframeMaterial = new THREE.LineBasicMaterial({
            color: 0x00ff00,
            transparent: true,
            opacity: 0.5
          });
          
          // Create wireframe object
          const wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
          
          // Apply the same transform as the original mesh
          wireframe.matrix.copy(child.matrixWorld);
          wireframe.matrixAutoUpdate = false;
          
          wireframeGroup.add(wireframe);
        }
      });
      
      if (wireframeGroup.children.length > 0) {
        wireframeGroup.userData.modelId = modelId;
        wireframeGroup.userData.isWireframeVisualization = true;
        
        scene.add(wireframeGroup);
        wireframeObjects.set(modelId, wireframeGroup);
      }
    };
    
    // NEW: Remove vertex visualization
    const removeVertexVisualization = () => {
      vertexPointClouds.forEach((pointCloud) => {
        scene.remove(pointCloud);
        pointCloud.geometry.dispose();
        pointCloud.material.dispose();
      });
      vertexPointClouds.clear();
    };
    
    // NEW: Remove wireframe visualization
    const removeWireframeVisualization = () => {
      wireframeObjects.forEach((wireframeGroup) => {
        scene.remove(wireframeGroup);
        wireframeGroup.traverse((child) => {
          if (child.geometry) child.geometry.dispose();
          if (child.material) child.material.dispose();
        });
      });
      wireframeObjects.clear();
    };
    
    // NEW: Update vertex visualization settings
    const updateVertexVisualization = () => {
      vertexPointClouds.forEach((pointCloud) => {
        pointCloud.material.color.setHex(vertexSettings.color.replace('#', '0x'));
        pointCloud.material.size = vertexSettings.size;
        pointCloud.material.opacity = vertexSettings.opacity;
      });
    };

    // NEW: Helper to emit material changes
    const emitMaterialChange = () => {
      if (!selectedObject.value) return;
      
      const modelId = selectedObject.value.userData.modelId;
      emit('model-material-changed', {
        modelId,
        material: {
          color: selectedObjectMaterial.value.color,
          roughness: selectedObjectMaterial.value.roughness,
          metalness: selectedObjectMaterial.value.metalness,
          emissive: selectedObjectMaterial.value.emissive,
          emissiveIntensity: selectedObjectMaterial.value.emissiveIntensity,
          textureId: selectedObjectMaterial.value.textureId
        }
      });
    };
    
    // NEW: Update model changes
    const updateModelChanges = async () => {
      if (!selectedObject.value || !editMode.value) return;
      
      // Get model ID from selected object
      const modelId = selectedObject.value.userData.modelId;
      if (!modelId) {
        showUpdateStatus('Error: Model ID not found', 'error');
        return;
      }
      
      // Collect current model parameters
      const updateData = {
        position: [
          selectedObject.value.position.x,
          selectedObject.value.position.y,
          selectedObject.value.position.z
        ],
        rotation: [
          selectedObject.value.rotation.x * (180/Math.PI), // Convert to degrees for API
          selectedObject.value.rotation.y * (180/Math.PI),
          selectedObject.value.rotation.z * (180/Math.PI)
        ],
        scale: [
          selectedObject.value.scale.x,
          selectedObject.value.scale.y,
          selectedObject.value.scale.z
        ],
        material: {
          color: selectedObjectMaterial.value.color,
          roughness: selectedObjectMaterial.value.roughness,
          metalness: selectedObjectMaterial.value.metalness,
          emissive: selectedObjectMaterial.value.emissive,
          emissiveIntensity: selectedObjectMaterial.value.emissiveIntensity
        }
      };
      
      isUpdating.value = true;
      showUpdateStatus('Processing model update...', 'info');
      
      try {
        const response = await axios.post(`/api/models/${modelId}/update`, updateData);
        
        if (response.data && response.data.updatedModel) {
          showUpdateStatus('Model updated successfully!', 'success');
          
          // Emit event to parent component
          emit('model-updated', {
            originalModelId: modelId,
            updatedModel: response.data.updatedModel
          });
        } else {
          showUpdateStatus('Update completed with warnings', 'warning');
        }
      } catch (error) {
        console.error('Error updating model:', error);
        showUpdateStatus(`Update failed: ${error.response?.data?.error || error.message}`, 'error');
      } finally {
        isUpdating.value = false;
        
        // Hide status message after 5 seconds
        setTimeout(() => {
          updateStatus.show = false;
        }, 5000);
      }
    };
    
    // NEW: Helper to show update status
    const showUpdateStatus = (message, type) => {
      updateStatus.show = true;
      updateStatus.message = message;
      updateStatus.type = type;
    };
    
    return {
      container,
      isLoading,
      showGrid,
      editMode,
      selectedObject,
      moveStep,
      selectedObjectMaterial,
      availableTextures,
      textureFileInput,
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
      updateMaterialProperty,
      updateMaterialRoughness,
      updateMaterialMetalness,
      handleTextureUpload,
      applySelectedTexture,
      getSelectedTextureUrl,
      getSelectedTextureName,
      onTexturePreviewError,
      showVertices,
      showWireframe,
      vertexSettings,
      toggleVertexVisualization,
      toggleWireframe,
      updateVertexVisualization,
      updateModelChanges,
      isUpdating,
      updateStatus
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
  bottom: 15px; /* Moved up slightly from 10px */
  left: 15px; /* Moved right slightly from 10px */
  display: flex;
  gap: 8px;
  z-index: 1000; /* High z-index to ensure visibility */
  flex-wrap: wrap; /* Allow wrapping on smaller screens */
  max-width: calc(100% - 30px); /* Prevent overflow */
}

.control-button {
  padding: 10px 14px; /* Slightly larger padding for better visibility */
  background-color: rgba(0, 0, 0, 0.8); /* More opaque for better visibility */
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3); /* Add border for definition */
  border-radius: 6px; /* Slightly larger radius */
  cursor: pointer;
  font-size: 13px; /* Slightly smaller font to fit better */
  transition: all 0.3s;
  font-weight: bold;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.4); /* Stronger shadow for visibility */
  white-space: nowrap; /* Prevent text wrapping */
}

.control-button:hover {
  background-color: rgba(0, 0, 0, 0.95);
  border-color: rgba(255, 255, 255, 0.6);
  transform: translateY(-2px); /* More pronounced lift on hover */
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.5);
}

.control-button.active {
  background-color: #ff6b00;
  border-color: #fff;
  box-shadow: 0 0 15px rgba(255, 107, 0, 0.6); /* Stronger glow effect */
}

.mouse-controls-info {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  max-width: 200px;
}

.controls-help h5 {
  margin: 0 0 8px 0;
  color: #ff6b00;
  font-size: 14px;
}

.controls-help ul {
  margin: 0;
  padding-left: 15px;
  list-style-type: disc;
}

.controls-help li {
  margin-bottom: 4px;
  line-height: 1.3;
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
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.control-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.control-section h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #333;
}

.axis-control {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.axis-control label {
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
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.direction-btn:hover {
  background-color: #f0f0f0;
}

.direction-btn:active {
  background-color: #2196f3;
  color: white;
}

.rotation-btn {
  background-color: #f8f9fa;
  border-color: #e3f2fd;
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

.control-hint {
  margin-bottom: 8px;
  font-size: 10px;
  color: #666;
  font-style: italic;
}

.control-hint span {
  background-color: #f0f8ff;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #e0e0e0;
}

.texture-selector {
  flex: 1;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 11px;
  background-color: white;
}

.texture-upload-input {
  padding: 2px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 10px;
  flex: 1;
}

.texture-preview {
  margin: 8px 0;
  text-align: center;
}

.texture-preview-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

/* NEW: Vertex visualization controls */
.vertex-controls {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 6px;
  font-size: 12px;
  max-width: 250px;
}

.vertex-settings h5 {
  margin: 0 0 8px 0;
  color: #ff6b00;
  font-size: 14px;
}

.control-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
}

.control-row label {
  min-width: 60px;
  font-size: 11px;
}

.vertex-slider {
  flex: 1;
  min-width: 80px;
}

.vertex-color-picker {
  cursor: pointer;
  border-radius: 3px;
  border: none;
  height: 20px;
  width: 30px;
}

.control-row span {
  text-align: right;
  font-size: 10px;
  min-width: 30px;
}

/* Update status styles */
.update-controls {
  margin-top: 15px;
}

.update-btn {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.update-btn:hover {
  background-color: #218838;
}

.update-btn:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.update-status {
  margin-top: 8px;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  text-align: center;
}

.update-status.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.update-status.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.update-status.warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.update-status.info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}
</style>