# Web 3D Application

This project consists of:

- A Vue.js frontend with TresJS for 3D rendering
- A Flask backend API

## Features

- **3D Model Viewing**: Support for .obj model format
- **Multi-Model Scenes**: Create scenes with multiple 3D models
- **Edit Mode**: Interactive object manipulation with directional controls
- **Model Management**: Upload, view, and delete 3D models
- **Real-time Controls**: Position and rotation adjustment using arrow controls or manual input

## Edit Mode

The 3D Scene Editor includes an interactive edit mode that allows you to:

- Click on objects to select them
- Use directional arrow buttons to move objects along X, Y, Z axes
- Rotate objects around X, Y, Z axes using rotation controls
- Adjust movement and rotation step sizes (0.1, 0.5, 1.0, 2.0 units)
- Reset object positions and rotations
- Visual highlighting of selected objects

**How to use Edit Mode:**

1. Go to "3D Scene Editor"
2. Add models to your scene
3. Click "Edit Mode" button in the 3D viewer
4. Click on any object to select it
5. Use the arrow controls in the edit panel to move the object
6. Use the rotation controls to rotate the object around each axis
7. Exit edit mode to return to normal camera controls

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
