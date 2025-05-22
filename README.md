# Web 3D Application

This project consists of:

- A Vue.js frontend with TresJS for 3D rendering
- A Flask backend API

## Project Structure

```
web-3d-app/
├── frontend/          # Vue.js with TresJS frontend
│   ├── public/        # Static assets
│   │   └── models/    # 3D model files (.glb, .gltf)
│   ├── src/           # Vue source code
│   │   ├── assets/    # Frontend assets (CSS, images)
│   │   ├── components/# Vue components
│   │   ├── router/    # Vue Router configuration
│   │   ├── views/     # Vue views (pages)
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
