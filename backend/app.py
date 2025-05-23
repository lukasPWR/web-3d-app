from flask import Flask, jsonify, request, send_from_directory, url_for, make_response
import os
import uuid
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
MODELS_FOLDER = os.path.join(app.root_path, 'static/models')
ALLOWED_EXTENSIONS = {'obj', 'gltf', 'glb', 'fbx'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size

# Ensure models directory exists
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Sample models
models = [
    {
        "id": "1",
        "name": "Car",
        "description": "A 3D model of a car",
        "modelUrl": "/models/car.obj",
        "format": "obj",
        "category": "vehicles"
    },
    {
        "id": "2",
        "name": "Roof Tile",
        "description": "A single roof tile",
        "modelUrl": "/models/roof_tile.obj",
        "format": "obj",
        "category": "construction"
    },
    {
        "id": "3",
        "name": "Cube",
        "description": "A simple 3D cube",
        "modelUrl": "/models/cube.obj",
        "format": "obj",
        "category": "basic"
    }
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/models', methods=['GET', 'OPTIONS'])
def get_models():
    """Returns list of all available 3D models"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # Optional category filter
    category = request.args.get('category')
    if category:
        filtered_models = [model for model in models if model.get('category') == category]
        return jsonify(filtered_models)
    
    return jsonify(models)

@app.route('/api/models/categories', methods=['GET', 'OPTIONS'])
def get_categories():
    """Returns list of all model categories"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    categories = set(model.get('category', 'uncategorized') for model in models)
    return jsonify(list(categories))

@app.route('/api/models/<model_id>', methods=['GET', 'OPTIONS'])
def get_model(model_id):
    """Returns details of a specific 3D model"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    model = next((model for model in models if model["id"] == model_id), None)
    if model:
        return jsonify(model)
    return jsonify({"error": "Model not found"}), 404

@app.route('/api/models/upload', methods=['POST', 'OPTIONS'])
def upload_model():
    """Handles 3D model file upload"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Secure filename and save file
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(MODELS_FOLDER, unique_filename)
    file.save(file_path)
    
    # Create new model entry
    new_model = {
        "id": str(uuid.uuid4()),
        "name": request.form.get("name", filename),
        "description": request.form.get("description", "Uploaded 3D model"),
        "modelUrl": f"/models/{unique_filename}",
        "format": file_extension,
        "category": request.form.get("category", "uncategorized")
    }
    
    models.append(new_model)
    return jsonify(new_model), 201

@app.route('/models/<path:filename>')
def serve_model(filename):
    """Serves 3D model files with proper MIME types"""
    mime_types = {
        'obj': 'application/octet-stream',
        'gltf': 'model/gltf+json',
        'glb': 'model/gltf-binary',
        'fbx': 'application/octet-stream'
    }
    
    extension = filename.split('.')[-1].lower()
    mime_type = mime_types.get(extension, 'application/octet-stream')
    
    response = make_response(send_from_directory(MODELS_FOLDER, filename))
    response.headers['Content-Type'] = mime_type
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/models/<model_id>', methods=['DELETE', 'OPTIONS'])
def delete_model(model_id):
    """Deletes a 3D model"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    model = next((model for model in models if model["id"] == model_id), None)
    if not model:
        return jsonify({"error": "Model not found"}), 404
    
    # Remove file if it exists
    try:
        filename = model["modelUrl"].split("/")[-1]
        file_path = os.path.join(MODELS_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error removing file: {e}")
    
    # Remove from models list
    models[:] = [m for m in models if m["id"] != model_id]
    
    return jsonify({"message": "Model deleted successfully"}), 200

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

@app.route('/')
def index():
    """Root endpoint to check if API is running"""
    return jsonify({
        "status": "API is running",
        "endpoints": {
            "GET /api/models": "List all models",
            "GET /api/models/categories": "List all model categories",
            "GET /api/models/<model_id>": "Get model details",
            "POST /api/models/upload": "Upload a new model",
            "DELETE /api/models/<model_id>": "Delete a model"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
