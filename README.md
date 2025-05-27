# Web 3D Application

A full-stack 3D model viewer application built with Vue.js frontend and Flask backend.

## Features

### 3D Model Viewer

- Support for multiple 3D formats (OBJ, GLTF, GLB, FBX)
- Interactive camera controls (orbit, zoom, pan)
- Multi-model scene composition
- Real-time lighting and shadows

### Advanced Edit Mode

- **Interactive Object Selection**: Click on models to select them
- **Mouse-based Manipulation**:
  - Drag to move objects in screen plane
  - Shift + Drag for rotation
  - Ctrl + Drag for Z-axis movement
  - Mouse wheel for scaling
- **Precision Controls Panel**:
  - Position adjustment using directional arrows or manual input
  - Scale modification with visual feedback
- **Advanced Material Editing**:
  - Color picker for base material color
  - Emissive color and intensity controls
  - Texture upload and application
  - Roughness and metalness controls
- **Step Size Control**: Adjustable movement increments (0.1, 0.5, 1.0, 2.0 units)
- **Reset Functions**: Reset position, rotation, or all transforms
- **Visual Feedback**: Selected objects are highlighted with distinctive materials

### Texture System

- Upload and apply textures to models
- Support for common image formats (JPG, PNG, BMP, TGA, TIFF)
- Real-time texture preview
- Texture scaling controls

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
   - Apply textures with upload functionality
7. Switch between objects by clicking them in the 3D view
8. Changes sync automatically between edit mode and model selector
9. Exit edit mode to return to normal camera controls

## Project Structure

```
web-3d-app/
├── frontend/          # Vue.js with Three.js frontend
│   ├── public/        # Static assets
│   │   └── models/    # 3D model files (.glb, .gltf)
│   ├── src/           # Vue source code
│   │   ├── assets/    # Frontend assets (CSS, images)
│   │   ├── components/# Vue components
│   │   │   ├── SimpleModelViewer.vue # 3D viewer with edit mode
│   │   │   ├── ModelSelector.vue     # Model selection and positioning
│   │   │   ├── ModelUploader.vue     # Model upload component
│   │   │   └── ModelList.vue         # Model listing component
│   │   ├── router/    # Vue Router configuration
│   │   ├── services/  # API service layer
│   │   │   └── api.js # Axios API client
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
    ├── static/        # Static file serving
    │   ├── models/    # Uploaded 3D models
    │   └── textures/  # Uploaded textures
    ├── app.py         # Main Flask application
    ├── requirements.txt # Python dependencies
    └── README.md      # Backend documentation
```

## Development Setup Instructions

### Prerequisites

- Node.js (version 14 or higher)
- Python 3.8 or higher
- Git

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a Python virtual environment:

   ```bash
   python -m venv venv
   ```

3. Activate the Python virtual environment:

   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the Flask development server:

   ```bash
   flask run
   ```

   The backend will run on http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:

   ```bash
   npm install
   ```

3. Start the Vite development server:

   ```bash
   npm run dev
   ```

   The frontend will run on http://localhost:5173

### Usage

1. Open your browser and navigate to http://localhost:5173
2. Upload 3D models using the "Upload New Model" button
3. Create scenes using the "Create 3D Scene" button
4. Use Edit Mode for advanced model manipulation
5. Apply textures and adjust material properties in real-time

### API Endpoints

The backend provides a RESTful API for model and texture management:

- **Models**: `/api/models` (GET, POST)
- **Individual Model**: `/api/models/<id>` (GET, DELETE)
- **Model Upload**: `/api/models/upload` (POST)
- **Textures**: `/api/textures` (GET, POST)
- **Texture Upload**: `/api/textures/upload` (POST)

### Troubleshooting

1. **404 errors for model files**: Ensure both backend and frontend servers are running
2. **CORS issues**: Check that the backend CORS configuration allows requests from the frontend
3. **File upload failures**: Verify the backend `static/models` and `static/textures` directories exist
