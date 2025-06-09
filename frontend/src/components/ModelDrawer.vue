<template>
  <div class="model-drawer">
    <div class="drawer-header">
      <h3>Programmatic Model Drawing</h3>
      <button @click="toggleDrawer" class="toggle-btn">
        {{ showDrawer ? 'Hide' : 'Show' }} Drawing Tools
      </button>
    </div>
    
    <div v-if="showDrawer" class="drawer-content">
      <!-- Quick Draw Section -->
      <div class="section">
        <h4>Quick Draw</h4>
        <div class="quick-draw-grid">
          <button @click="drawPrimitive('cube')" class="draw-btn primitive-btn">
            📦 Draw Cube
          </button>
          <button @click="drawPrimitive('sphere')" class="draw-btn primitive-btn">
            🌐 Draw Sphere
          </button>
          <button @click="drawPrimitive('cylinder')" class="draw-btn primitive-btn">
            🛢️ Draw Cylinder
          </button>
          <button @click="drawPrimitive('cone')" class="draw-btn primitive-btn">
            📐 Draw Cone
          </button>
          <button @click="showLineDrawer = true" class="draw-btn line-btn">
            📏 Draw Line
          </button>
          <button @click="showAdvancedDrawer = true" class="draw-btn advanced-btn">
            ⚙️ Advanced Drawing
          </button>
        </div>
      </div>
      
      <!-- Line Drawing Section -->
      <div v-if="showLineDrawer" class="section">
        <h4>Line Drawing</h4>
        <div class="line-drawing-form">
          <div class="form-group">
            <label>Line Name:</label>
            <input v-model="lineParams.name" type="text" placeholder="My Line" class="form-input">
          </div>
          
          <div class="form-group">
            <label>Line Color:</label>
            <input v-model="lineParams.color" type="color" class="color-input">
          </div>
          
          <div class="form-group">
            <label>Thickness:</label>
            <input v-model.number="lineParams.thickness" type="range" min="0.001" max="0.1" step="0.001" class="range-input">
            <span>{{ lineParams.thickness }}</span>
          </div>
          
          <div class="form-group">
            <label>Points:</label>
            <div class="points-list">
              <div v-for="(point, index) in lineParams.points" :key="index" class="point-input">
                <span>Point {{ index + 1 }}:</span>
                <input v-model.number="point.x" type="number" placeholder="X" step="0.1" class="coord-input">
                <input v-model.number="point.y" type="number" placeholder="Y" step="0.1" class="coord-input">
                <input v-model.number="point.z" type="number" placeholder="Z" step="0.1" class="coord-input">
                <button @click="removePoint(index)" class="remove-btn" v-if="lineParams.points.length > 2">❌</button>
              </div>
            </div>
            <button @click="addPoint" class="add-btn">➕ Add Point</button>
          </div>
          
          <div class="form-actions">
            <button @click="drawLine" class="draw-btn" :disabled="isDrawing">
              {{ isDrawing ? 'Drawing...' : 'Draw Line' }}
            </button>
            <button @click="showLineDrawer = false" class="cancel-btn">Cancel</button>
          </div>
        </div>
      </div>
      
      <!-- Advanced Drawing Section -->
      <div v-if="showAdvancedDrawer" class="section">
        <h4>Advanced Drawing Session</h4>
        <div class="advanced-drawing-form">
          <div class="form-group">
            <label>Session Name:</label>
            <input v-model="sessionParams.name" type="text" placeholder="My Drawing Session" class="form-input">
          </div>
          
          <div class="form-group">
            <label>
              <input v-model="sessionParams.clearScene" type="checkbox">
              Clear scene before drawing
            </label>
          </div>
          
          <div class="commands-section">
            <h5>Drawing Commands</h5>
            <div v-for="(command, index) in sessionParams.commands" :key="index" class="command-item">
              <div class="command-header">
                <span>{{ command.type.toUpperCase() }} Command {{ index + 1 }}</span>
                <button @click="removeCommand(index)" class="remove-btn">Remove</button>
              </div>
              
              <!-- Primitive Command -->
              <div v-if="command.type === 'primitive'" class="command-form">
                <select v-model="command.data.primitive_type" class="form-input">
                  <option value="cube">Cube</option>
                  <option value="sphere">Sphere</option>
                  <option value="cylinder">Cylinder</option>
                  <option value="cone">Cone</option>
                  <option value="plane">Plane</option>
                  <option value="torus">Torus</option>
                </select>
                
                <div class="position-controls">
                  <label>Position:</label>
                  <input v-model.number="command.data.location.x" type="number" placeholder="X" step="0.1" class="coord-input">
                  <input v-model.number="command.data.location.y" type="number" placeholder="Y" step="0.1" class="coord-input">
                  <input v-model.number="command.data.location.z" type="number" placeholder="Z" step="0.1" class="coord-input">
                </div>
                
                <div class="scale-controls">
                  <label>Scale:</label>
                  <input v-model.number="command.data.scale.x" type="number" placeholder="X" step="0.1" min="0.1" class="coord-input">
                  <input v-model.number="command.data.scale.y" type="number" placeholder="Y" step="0.1" min="0.1" class="coord-input">
                  <input v-model.number="command.data.scale.z" type="number" placeholder="Z" step="0.1" min="0.1" class="coord-input">
                </div>
                
                <div class="color-control">
                  <label>Color:</label>
                  <input v-model="command.data.color" type="color" class="color-input">
                </div>
                
                <div class="name-control">
                  <label>Name:</label>
                  <input v-model="command.data.name" type="text" class="form-input">
                </div>
              </div>
            </div>
            
            <div class="add-command-section">
              <button @click="addPrimitiveCommand" class="add-btn">➕ Add Primitive</button>
              <button @click="addLineCommand" class="add-btn">➕ Add Line</button>
            </div>
          </div>
          
          <div class="form-actions">
            <button @click="executeDrawingSession" class="draw-btn" :disabled="isDrawing || sessionParams.commands.length === 0">
              {{ isDrawing ? 'Drawing...' : 'Execute Drawing Session' }}
            </button>
            <button @click="showAdvancedDrawer = false" class="cancel-btn">Cancel</button>
          </div>
        </div>
      </div>
      
      <!-- Drawing Status -->
      <div v-if="isDrawing" class="drawing-status">
        <div class="spinner"></div>
        <p>Creating your 3D model... This may take a moment.</p>
      </div>
      
      <!-- Success/Error Messages -->
      <div v-if="drawingResult" class="drawing-result">
        <div v-if="drawingResult.success" class="success-message">
          ✅ Model "{{ drawingResult.model.name }}" created successfully!
          <button @click="addModelToScene(drawingResult.model)" class="add-to-scene-btn">
            Add to Scene
          </button>
        </div>
        <div v-else class="error-message">
          ❌ Drawing failed: {{ drawingResult.error }}
        </div>
        <button @click="drawingResult = null" class="close-result-btn">×</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import api from '../services/api.js';

export default {
  name: 'ModelDrawer',
  emits: ['model-created'],
  setup(props, { emit }) {
    const showDrawer = ref(false);
    const showLineDrawer = ref(false);
    const showAdvancedDrawer = ref(false);
    const isDrawing = ref(false);
    const drawingResult = ref(null);
    
    // Line drawing parameters
    const lineParams = reactive({
      name: 'My Line',
      color: '#ffffff',
      thickness: 0.01,
      points: [
        { x: 0, y: 0, z: 0 },
        { x: 1, y: 1, z: 0 }
      ]
    });
    
    // Advanced session parameters
    const sessionParams = reactive({
      name: 'My Drawing Session',
      clearScene: true,
      commands: []
    });
    
    const toggleDrawer = () => {
      showDrawer.value = !showDrawer.value;
    };
    
    // Quick primitive drawing
    const drawPrimitive = async (primitiveType) => {
      isDrawing.value = true;
      drawingResult.value = null;
      
      try {
        const response = await api.drawPrimitive(primitiveType, [0, 0, 0], [1, 1, 1], '#8080ff', `${primitiveType.charAt(0).toUpperCase() + primitiveType.slice(1)}_Generated`);
        
        drawingResult.value = {
          success: true,
          model: response.data.model
        };
        
        emit('model-created', response.data.model);
        
      } catch (error) {
        console.error('Primitive drawing error:', error);
        drawingResult.value = {
          success: false,
          error: error.response?.data?.detail || error.message
        };
      } finally {
        isDrawing.value = false;
      }
    };
    
    // Line drawing functions
    const addPoint = () => {
      lineParams.points.push({ x: 0, y: 0, z: 0 });
    };
    
    const removePoint = (index) => {
      if (lineParams.points.length > 2) {
        lineParams.points.splice(index, 1);
      }
    };
    
    const drawLine = async () => {
      if (lineParams.points.length < 2) {
        alert('Line requires at least 2 points');
        return;
      }
      
      isDrawing.value = true;
      drawingResult.value = null;
      
      try {
        const points = lineParams.points.map(p => [p.x, p.y, p.z]);
        const response = await api.drawLine(points, lineParams.color, lineParams.thickness, lineParams.name);
        
        drawingResult.value = {
          success: true,
          model: response.data.model
        };
        
        emit('model-created', response.data.model);
        showLineDrawer.value = false;
        
      } catch (error) {
        console.error('Line drawing error:', error);
        drawingResult.value = {
          success: false,
          error: error.response?.data?.detail || error.message
        };
      } finally {
        isDrawing.value = false;
      }
    };
    
    // Advanced session functions
    const addPrimitiveCommand = () => {
      sessionParams.commands.push({
        type: 'primitive',
        data: {
          primitive_type: 'cube',
          location: { x: 0, y: 0, z: 0 },
          scale: { x: 1, y: 1, z: 1 },
          rotation: { x: 0, y: 0, z: 0 },
          color: '#8080ff',
          name: `Primitive_${sessionParams.commands.length + 1}`
        }
      });
    };
    
    const addLineCommand = () => {
      sessionParams.commands.push({
        type: 'line',
        data: {
          points: [
            { x: 0, y: 0, z: 0 },
            { x: 1, y: 1, z: 0 }
          ],
          color: '#ffffff',
          thickness: 0.01,
          name: `Line_${sessionParams.commands.length + 1}`
        }
      });
    };
    
    const removeCommand = (index) => {
      sessionParams.commands.splice(index, 1);
    };
    
    const executeDrawingSession = async () => {
      if (sessionParams.commands.length === 0) {
        alert('Add at least one drawing command');
        return;
      }
      
      isDrawing.value = true;
      drawingResult.value = null;
      
      try {
        const sessionData = {
          session_id: `session_${Date.now()}`,
          clear_scene: sessionParams.clearScene,
          commands: sessionParams.commands.map(cmd => [cmd.type, cmd.data]),
          output_format: 'obj',
          output_name: sessionParams.name
        };
        
        const response = await api.executeDrawingSession(sessionData);
        
        drawingResult.value = {
          success: true,
          model: response.data.model
        };
        
        emit('model-created', response.data.model);
        showAdvancedDrawer.value = false;
        
      } catch (error) {
        console.error('Drawing session error:', error);
        drawingResult.value = {
          success: false,
          error: error.response?.data?.detail || error.message
        };
      } finally {
        isDrawing.value = false;
      }
    };
    
    const addModelToScene = (model) => {
      // This would trigger adding the model to the current scene
      emit('model-created', model);
      drawingResult.value = null;
    };
    
    return {
      showDrawer,
      showLineDrawer,
      showAdvancedDrawer,
      isDrawing,
      drawingResult,
      lineParams,
      sessionParams,
      toggleDrawer,
      drawPrimitive,
      addPoint,
      removePoint,
      drawLine,
      addPrimitiveCommand,
      addLineCommand,
      removeCommand,
      executeDrawingSession,
      addModelToScene
    };
  }
};
</script>

<style scoped>
.model-drawer {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 10px 0;
}

.drawer-header {
  padding: 15px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e9ecef;
  border-radius: 8px 8px 0 0;
}

.drawer-header h3 {
  margin: 0;
  color: #333;
}

.toggle-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.toggle-btn:hover {
  background-color: #0056b3;
}

.drawer-content {
  padding: 20px;
}

.section {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.section:last-child {
  border-bottom: none;
}

.section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.quick-draw-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.draw-btn {
  padding: 12px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.3s;
}

.primitive-btn {
  background-color: #28a745;
  color: white;
}

.primitive-btn:hover {
  background-color: #218838;
}

.line-btn {
  background-color: #17a2b8;
  color: white;
}

.line-btn:hover {
  background-color: #138496;
}

.advanced-btn {
  background-color: #6f42c1;
  color: white;
}

.advanced-btn:hover {
  background-color: #5a32a3;
}

.line-drawing-form, .advanced-drawing-form {
  background-color: white;
  padding: 20px;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-input, .color-input, .range-input, .coord-input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-input {
  width: 100%;
}

.coord-input {
  width: 80px;
  margin-right: 5px;
}

.points-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.point-input {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.commands-section {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  background-color: #f9f9f9;
}

.command-item {
  margin-bottom: 15px;
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.command-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.position-controls, .scale-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.add-btn, .remove-btn, .cancel-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.add-btn {
  background-color: #28a745;
  color: white;
}

.remove-btn {
  background-color: #dc3545;
  color: white;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.drawing-status {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background-color: #e3f2fd;
  border-radius: 6px;
  margin: 15px 0;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.drawing-result {
  position: relative;
  padding: 15px;
  border-radius: 6px;
  margin: 15px 0;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
  padding: 15px;
  border-radius: 4px;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  padding: 15px;
  border-radius: 4px;
}

.add-to-scene-btn {
  margin-left: 10px;
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.close-result-btn {
  position: absolute;
  top: 5px;
  right: 10px;
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
}
</style>
