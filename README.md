# Web 3D Application

This project consists of:

- A Vue.js frontend with TresJS for 3D rendering
- A Flask backend API

## Features

- **3D Model Viewing**: Support for multiple 3D model formats (.obj, .gltf, .glb, .fbx)
- **Multi-Model Scenes**: Create scenes with multiple 3D models with full individual editing capabilities
- **Advanced Edit Mode**: Interactive object manipulation with comprehensive controls:
  - Individual model selection and editing
  - Real-time position, rotation, and scale adjustments
  - Material property editing (color, roughness, metalness, emission)
  - Visual highlighting of selected objects
  - Directional arrow controls and manual input
- **Model Management**: Upload, view, organize, and delete 3D models
- **Dual Control Interface**:
  - Edit mode for precise interactive manipulation
  - Model selector panel for bulk property adjustments
- **Real-time Synchronization**: Changes made in edit mode sync with model selector and vice versa

## Enhanced Edit Mode

The 3D Scene Editor now features a comprehensive edit mode that allows you to:

- **Multi-Model Management**: Add multiple models to a single scene
- **Individual Model Editing**: Click on any object to select and edit it independently
- **Comprehensive Transform Controls**:
  - Position adjustment using directional arrows or manual input
  - Rotation controls around all three axes
  - Scale modification with visual feedback
- **Advanced Material Editing**:
  - Color picker for base material color
  - Roughness slider (0.0 - 1.0)
  - Metalness adjustment (0.0 - 1.0)
  - Emissive color and intensity controls
- **Step Size Control**: Adjustable movement increments (0.1, 0.5, 1.0, 2.0 units)
- **Reset Functions**: Reset position, rotation, or all transforms
- **Visual Feedback**: Selected objects are highlighted with distinctive materials

**Enhanced Workflow:**

1. Go to "3D Scene Editor"
2. Add multiple models to your scene using the model selector
3. Use the model selector panel to set initial properties for each model
4. Click "Edit Mode" in the 3D viewer for interactive editing
5. Click on any object in the 3D scene to select it
6. Use the comprehensive edit panel to fine-tune:
   - Position using arrow controls or direct input
   - Rotation around each axis
   - Scale with +/- buttons
   - Material properties with sliders and color pickers
7. Switch between objects by clicking them in the 3D view
8. Changes sync automatically between edit mode and model selector
9. Exit edit mode to return to normal camera controls

## Project Structure

```
web-3d-app/
├── frontend/          # Vue.js with TresJS frontend
│   ├── public/        # Static assets
│   │   └── models/    # 3D model files (.glb, .gltf)
│   ├── src/           # Vue source code
│   │   ├── assets/    # Frontend assets (CSS, images)
│   │   ├── components/# Vue components
│   │   │   ├── SimpleModelViewer.vue # 3D viewer with edit mode
│   │   │   └── ModelSelector.vue     # Model selection and positioning
│   │   ├── router/    # Vue Router configuration
│   │   ├── views/     # Vue views (pages)
│   │   │   ├── HomeView.vue    # Main page
│   │   │   ├── SceneView.vue   # 3D Scene Editor
│   │   │   └── ModelView.vue   # Individual model viewer
│   │   ├── App.vue    # Root Vue component
│   │   └── main.js    # Vue application entry point
│   ├── index.html     # HTML entry point
│   ├── package.json   # Frontend dependencies
│   └── vite.config.js # Vite configuration
└── backend/           # Flask Python backend
    ├── app.py         # Main Flask application
    ├── venv/          # Python virtual environment
    └── requirements.txt # Python dependencies
```

## Development Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```
   cd backend
   ```

2. Activate the Python virtual environment:

   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Start the Flask development server:
   ```
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```
   The frontend will run on http://localhost:5173

## Adding 3D Models

Place your 3D models (.glb, .gltf) in the `frontend/public/models/` directory and update the model list in the backend's `app.py` file.
