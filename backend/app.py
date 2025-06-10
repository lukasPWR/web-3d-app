from flask import Flask, jsonify, request, send_from_directory, url_for, make_response
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS
import shutil
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app first
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
MODELS_FOLDER = os.path.join(app.root_path, 'static/models')
TEXTURES_FOLDER = os.path.join(app.root_path, 'static/textures')
MODELS_DB_FILE = os.path.join(MODELS_FOLDER, 'models_db.json')
TEXTURES_DB_FILE = os.path.join(TEXTURES_FOLDER, 'textures_db.json')
ALLOWED_EXTENSIONS = {'obj', 'gltf', 'glb', 'fbx'}
ALLOWED_TEXTURE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tga', 'tiff'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size

# Ensure directories exist
os.makedirs(MODELS_FOLDER, exist_ok=True)
os.makedirs(TEXTURES_FOLDER, exist_ok=True)

# Helper functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_texture_file(filename):
    """Check if texture file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TEXTURE_EXTENSIONS

# Initialize Blender service after app creation
try:
    from blender_service import BlenderDrawingService
    blender_service = BlenderDrawingService()
    logger.info("Blender service initialized successfully")
except ImportError as e:
    logger.error(f"Failed to import BlenderDrawingService: {e}")
    blender_service = None
except Exception as e:
    logger.error(f"Failed to initialize Blender service: {e}")
    blender_service = None

# Sample models
models = []

# Textures storage
textures = []

def load_models_from_storage():
    """Load models metadata from JSON file"""
    global models
    try:
        if os.path.exists(MODELS_DB_FILE):
            with open(MODELS_DB_FILE, 'r', encoding='utf-8') as f:
                models = json.load(f)
                logger.info(f"Loaded {len(models)} models from database")
        else:
            models = []
            logger.info("No existing models database found")
    except Exception as e:
        logger.error(f"Error loading models database: {e}")
        models = []

def save_models_to_storage():
    """Save models metadata to JSON file"""
    try:
        with open(MODELS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(models, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(models)} models to database")
    except Exception as e:
        logger.error(f"Error saving models database: {e}")

def load_textures_from_storage():
    """Load textures metadata from JSON file"""
    global textures
    try:
        if os.path.exists(TEXTURES_DB_FILE):
            with open(TEXTURES_DB_FILE, 'r', encoding='utf-8') as f:
                textures = json.load(f)
                logger.info(f"Loaded {len(textures)} textures from database")
        else:
            textures = []
            logger.info("No existing textures database found")
    except Exception as e:
        logger.error(f"Error loading textures database: {e}")
        textures = []

def save_textures_to_storage():
    """Save textures metadata to JSON file"""
    try:
        with open(TEXTURES_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(textures, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(textures)} textures to database")
    except Exception as e:
        logger.error(f"Error saving textures database: {e}")

def scan_and_load_existing_models():
    """Scan models folder and add any new files not in database"""
    global models
    
    if not os.path.exists(MODELS_FOLDER):
        return
    
    # Get list of files already in database
    existing_filenames = set()
    for model in models:
        if 'modelUrl' in model:
            filename = model['modelUrl'].split('/')[-1]
            existing_filenames.add(filename)
    
    # Scan folder for files
    added_count = 0
    for filename in os.listdir(MODELS_FOLDER):
        if filename.lower().endswith(('.obj', '.gltf', '.glb', '.fbx')):
            if filename not in existing_filenames:
                # File exists but not in database - add it
                file_path = os.path.join(MODELS_FOLDER, filename)
                file_stats = os.stat(file_path)
                
                # Try to extract original name from filename
                original_name = filename
                if '_' in filename:
                    # If filename contains UUID prefix, try to extract original name
                    parts = filename.split('_', 1)
                    if len(parts) > 1:
                        original_name = parts[1]
                
                # Remove file extension for display name
                display_name = os.path.splitext(original_name)[0]
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                new_model = {
                    "id": str(uuid.uuid4()),
                    "name": display_name,
                    "description": f"Model loaded from file: {original_name}",
                    "modelUrl": f"/models/{filename}",
                    "format": file_extension,
                    "category": "loaded",
                    "fileSize": file_stats.st_size,
                    "createdAt": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "isGenerated": False
                }
                
                models.append(new_model)
                added_count += 1
                logger.info(f"Added existing model: {display_name}")
    
    if added_count > 0:
        save_models_to_storage()
        logger.info(f"Added {added_count} existing model files to database")

def scan_and_load_existing_textures():
    """Scan textures folder and add any new files not in database"""
    global textures
    
    if not os.path.exists(TEXTURES_FOLDER):
        return
    
    # Get list of files already in database
    existing_filenames = set()
    for texture in textures:
        if 'textureUrl' in texture:
            filename = texture['textureUrl'].split('/')[-1]
            existing_filenames.add(filename)
    
    # Scan folder for files
    added_count = 0
    for filename in os.listdir(TEXTURES_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tga', '.tiff')):
            if filename not in existing_filenames:
                # File exists but not in database - add it
                file_path = os.path.join(TEXTURES_FOLDER, filename)
                file_stats = os.stat(file_path)
                
                # Try to extract original name from filename
                original_name = filename
                if '_' in filename:
                    parts = filename.split('_', 1)
                    if len(parts) > 1:
                        original_name = parts[1]
                
                # Remove file extension for display name
                display_name = os.path.splitext(original_name)[0]
                file_extension = filename.rsplit('.', 1)[1].lower()
                
                new_texture = {
                    "id": str(uuid.uuid4()),
                    "name": display_name,
                    "description": f"Texture loaded from file: {original_name}",
                    "textureUrl": f"/textures/{filename}",
                    "format": file_extension,
                    "type": "diffuse",
                    "category": "loaded",
                    "fileSize": file_stats.st_size,
                    "createdAt": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                }
                
                textures.append(new_texture)
                added_count += 1
                logger.info(f"Added existing texture: {display_name}")
    
    if added_count > 0:
        save_textures_to_storage()
        logger.info(f"Added {added_count} existing texture files to database")

def cleanup_missing_files():
    """Remove database entries for files that no longer exist"""
    global models, textures
    
    # Check models
    models_to_remove = []
    for model in models:
        if 'modelUrl' in model:
            filename = model['modelUrl'].split('/')[-1]
            file_path = os.path.join(MODELS_FOLDER, filename)
            if not os.path.exists(file_path):
                models_to_remove.append(model)
                logger.info(f"Removing missing model: {model['name']}")
    
    for model in models_to_remove:
        models.remove(model)
    
    # Check textures
    textures_to_remove = []
    for texture in textures:
        if 'textureUrl' in texture:
            filename = texture['textureUrl'].split('/')[-1]
            file_path = os.path.join(TEXTURES_FOLDER, filename)
            if not os.path.exists(file_path):
                textures_to_remove.append(texture)
                logger.info(f"Removing missing texture: {texture['name']}")
    
    for texture in textures_to_remove:
        textures.remove(texture)
    
    # Save changes if any files were removed
    if models_to_remove:
        save_models_to_storage()
    if textures_to_remove:
        save_textures_to_storage()

def initialize_storage():
    """Initialize storage system - load existing data and scan for new files"""
    logger.info("Initializing storage system...")
    
    # Load existing databases
    load_models_from_storage()
    load_textures_from_storage()
    
    # Clean up missing files first
    cleanup_missing_files()
    
    # Scan for new files
    scan_and_load_existing_models()
    scan_and_load_existing_textures()
    
    logger.info(f"Storage initialized: {len(models)} models, {len(textures)} textures")

# Initialize storage system before starting the app
initialize_storage()

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
    
    # Get file stats
    file_stats = os.stat(file_path)
    
    # Create new model entry
    new_model = {
        "id": str(uuid.uuid4()),
        "name": request.form.get("name", os.path.splitext(filename)[0]),
        "description": request.form.get("description", "Uploaded 3D model"),
        "modelUrl": f"/models/{unique_filename}",
        "format": file_extension,
        "category": request.form.get("category", "uploaded"),
        "fileSize": file_stats.st_size,
        "createdAt": datetime.now().isoformat(),
        "isGenerated": False
    }
    
    models.append(new_model)
    save_models_to_storage()  # Save to persistent storage
    return jsonify(new_model), 201

@app.route('/models/<path:filename>')
def serve_model(filename):
    """Serves 3D model files with proper MIME types"""
    try:
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
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except FileNotFoundError:
        return jsonify({"error": f"Model file {filename} not found"}), 404
    except Exception as e:
        print(f"Error serving model {filename}: {e}")
        return jsonify({"error": "Internal server error"}), 500

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
        logger.error(f"Error removing file: {e}")
    
    # Remove from models list
    models[:] = [m for m in models if m["id"] != model_id]
    save_models_to_storage()  # Save changes
    
    return jsonify({"message": "Model deleted successfully"}), 200

@app.route('/api/textures', methods=['GET', 'OPTIONS'])
def get_textures():
    """Returns list of all available textures"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    return jsonify(textures)

@app.route('/api/textures/upload', methods=['POST', 'OPTIONS'])
def upload_texture():
    """Handles texture file upload"""
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
    if not allowed_texture_file(file.filename):
        return jsonify({"error": f"File type not allowed. Supported formats: {', '.join(ALLOWED_TEXTURE_EXTENSIONS)}"}), 400
    
    # Secure filename and save file
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(TEXTURES_FOLDER, unique_filename)
    file.save(file_path)
    
    # Get file stats
    file_stats = os.stat(file_path)
    
    # Create new texture entry
    new_texture = {
        "id": str(uuid.uuid4()),
        "name": request.form.get("name", os.path.splitext(filename)[0]),
        "description": request.form.get("description", "Uploaded texture"),
        "textureUrl": f"/textures/{unique_filename}",
        "format": file_extension,
        "type": request.form.get("type", "diffuse"),
        "category": request.form.get("category", "uploaded"),
        "fileSize": file_stats.st_size,
        "createdAt": datetime.now().isoformat()
    }
    
    textures.append(new_texture)
    save_textures_to_storage()  # Save to persistent storage
    return jsonify(new_texture), 201

@app.route('/textures/<path:filename>')
def serve_texture(filename):
    """Serves texture files with proper MIME types"""
    try:
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'bmp': 'image/bmp',
            'tga': 'image/tga',
            'tiff': 'image/tiff'
        }
        
        extension = filename.split('.')[-1].lower()
        mime_type = mime_types.get(extension, 'image/jpeg')
        
        response = make_response(send_from_directory(TEXTURES_FOLDER, filename))
        response.headers['Content-Type'] = mime_type
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except FileNotFoundError:
        return jsonify({"error": f"Texture file {filename} not found"}), 404
    except Exception as e:
        print(f"Error serving texture {filename}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/textures/<texture_id>', methods=['DELETE', 'OPTIONS'])
def delete_texture(texture_id):
    """Deletes a texture"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    texture = next((texture for texture in textures if texture["id"] == texture_id), None)
    if not texture:
        return jsonify({"error": "Texture not found"}), 404
    
    # Remove file if it exists
    try:
        filename = texture["textureUrl"].split("/")[-1]
        file_path = os.path.join(TEXTURES_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error removing texture file: {e}")
    
    # Remove from textures list
    textures[:] = [t for t in textures if t["id"] != texture_id]
    save_textures_to_storage()  # Save changes
    
    return jsonify({"message": "Texture deleted successfully"}), 200

def cleanup_generated_files(output_path: str, dest_path: str):
    """
    Clean up generated files and copy them to destination.
    Removes orphaned MTL files and cleans OBJ references.
    
    Args:
        output_path: Source file path
        dest_path: Destination file path
    """
    try:
        # Copy main file
        shutil.copy2(output_path, dest_path)
        
        # Handle MTL files for OBJ exports
        if output_path.endswith('.obj'):
            source_mtl = output_path.replace('.obj', '.mtl')
            dest_mtl = dest_path.replace('.obj', '.mtl')
            
            # Copy MTL file if it exists and has content
            if os.path.exists(source_mtl):
                try:
                    with open(source_mtl, 'r') as f:
                        mtl_content = f.read().strip()
                    
                    # Check if MTL has actual material definitions
                    if 'newmtl' in mtl_content and len(mtl_content.split('\n')) > 5:
                        shutil.copy2(source_mtl, dest_mtl)
                        logger.info(f"Copied MTL file: {dest_mtl}")
                    else:
                        logger.info(f"Skipped empty MTL file: {source_mtl}")
                except Exception as e:
                    logger.warning(f"Error handling MTL file: {e}")
        
        logger.info(f"Successfully copied files to: {dest_path}")
            
    except Exception as e:
        logger.error(f"Error in cleanup_generated_files: {e}")
        raise

@app.route('/api/draw/session', methods=['POST', 'OPTIONS'])
def execute_drawing_session():
    """Execute a complete drawing session using Blender"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not blender_service:
        return jsonify({"success": False, "error": "Blender service not available"}), 503
    
    try:
        session_data = request.get_json()
        if not session_data:
            return jsonify({"error": "No session data provided"}), 400
        
        logger.info(f"Received drawing session request: {json.dumps(session_data, indent=2)}")
        
        success, output_path, error = blender_service.execute_drawing_session(session_data)
        
        if success and output_path:
            # Copy the generated file to our models directory
            filename = os.path.basename(output_path)
            dest_path = os.path.join(MODELS_FOLDER, filename)
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = os.stat(dest_path)
            
            # Create model entry
            new_model = {
                "id": str(uuid.uuid4()),
                "name": session_data.get("output_name", "Generated Model"),
                "description": "Generated using Blender drawing commands",
                "modelUrl": f"/models/{filename}",
                "format": session_data.get("output_format", "obj"),
                "category": "generated",
                "fileSize": file_stats.st_size,
                "createdAt": datetime.now().isoformat(),
                "isGenerated": True
            }
            
            models.append(new_model)
            save_models_to_storage()
            
            logger.info(f"Successfully created drawing session model: {new_model}")
            
            return jsonify({
                "success": True,
                "model": new_model,
                "session_id": session_data.get("session_id")
            }), 201
        else:
            logger.error(f"Drawing session failed: {error}")
            return jsonify({
                "success": False,
                "error": error or "Unknown drawing error"
            }), 500
            
    except Exception as e:
        logger.error(f"Exception in drawing session: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Drawing session failed: {str(e)}"
        }), 500

@app.route('/api/draw/line', methods=['POST', 'OPTIONS'])
def draw_line_endpoint():
    """Draw a simple line"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not blender_service:
        return jsonify({"success": False, "error": "Blender service not available"}), 503
    
    try:
        data = request.get_json()
        points = data.get('points', [])
        color = data.get('color', '#ffffff')
        thickness = data.get('thickness', 0.01)
        name = data.get('name', 'Line')
        
        if len(points) < 2:
            return jsonify({"error": "At least 2 points required"}), 400
        
        success, output_path, error = blender_service.create_line(points, color, thickness, name)
        
        if success and output_path:
            # Copy to models directory
            filename = os.path.basename(output_path)
            dest_path = os.path.join(MODELS_FOLDER, filename)
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = os.stat(dest_path)
            
            # Create model entry
            new_model = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": f"Line drawing with {len(points)} points",
                "modelUrl": f"/models/{filename}",
                "format": "obj",
                "category": "generated",
                "fileSize": file_stats.st_size,
                "createdAt": datetime.now().isoformat(),
                "isGenerated": True
            }
            
            models.append(new_model)
            save_models_to_storage()
            
            return jsonify({"success": True, "model": new_model}), 201
        else:
            return jsonify({"success": False, "error": error}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/draw/primitive', methods=['POST', 'OPTIONS'])
def draw_primitive_endpoint():
    """Draw a primitive shape"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not blender_service:
        return jsonify({"success": False, "error": "Blender service not available"}), 503
    
    try:
        data = request.get_json()
        logger.info(f"Received primitive drawing request: {data}")
        
        primitive_type = data.get('primitive_type', 'cube')
        location = data.get('location', [0, 0, 0])
        scale = data.get('scale', [1, 1, 1])
        color = data.get('color', '#8080ff')
        name = data.get('name', f'{primitive_type.title()}_Generated')
        
        success, output_path, error = blender_service.create_primitive(
            primitive_type, location, scale, color, name
        )
        
        if success and output_path:
            # Copy to models directory with cleanup
            filename = os.path.basename(output_path)
            dest_path = os.path.join(MODELS_FOLDER, filename)
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = os.stat(dest_path)
            
            # Create model entry
            new_model = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": f"Generated {primitive_type}",
                "modelUrl": f"/models/{filename}",
                "format": "obj",
                "category": "generated",
                "fileSize": file_stats.st_size,
                "createdAt": datetime.now().isoformat(),
                "isGenerated": True
            }
            
            models.append(new_model)
            save_models_to_storage()  # Save to persistent storage
            logger.info(f"Successfully created primitive: {new_model}")
            return jsonify({"success": True, "model": new_model}), 201
        else:
            logger.error(f"Primitive creation failed: {error}")
            return jsonify({"success": False, "error": error}), 500
            
    except Exception as e:
        logger.error(f"Exception in primitive drawing: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500



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
            "DELETE /api/models/<model_id>": "Delete a model",
            "GET /api/textures": "List all textures",
            "POST /api/textures/upload": "Upload a new texture",
            "DELETE /api/textures/<texture_id>": "Delete a texture",
            "POST /api/draw/session": "Execute a drawing session",
            "POST /api/draw/line": "Draw a line",
            "POST /api/draw/primitive": "Draw a primitive shape",
            "POST /api/admin/cleanup": "Clean up output folder"
        }
    })

# Add OPTIONS handlers for model and texture routes
@app.route('/models/<path:filename>', methods=['OPTIONS'])
def options_model(filename):
    return _build_cors_preflight_response()

@app.route('/textures/<path:filename>', methods=['OPTIONS'])
def options_texture(filename):
    return _build_cors_preflight_response()

def cleanup_output_drawings_folder():
    """
    Clean up the output/drawings folder by removing all generated files.
    This is a more aggressive cleanup that removes everything.
    """
    try:
        output_drawings_path = os.path.join(os.path.dirname(__file__), 'output', 'drawings')
        
        if not os.path.exists(output_drawings_path):
            logger.info("Output drawings folder does not exist")
            return
        
        files_removed = 0
        total_files = 0
        
        # Remove all files in the directory
        for item in os.listdir(output_drawings_path):
            item_path = os.path.join(output_drawings_path, item)
            total_files += 1
            
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    files_removed += 1
                    logger.info(f"Removed file: {item}")
                elif os.path.isdir(item_path):
                    # Remove directory and all contents
                    shutil.rmtree(item_path)
                    files_removed += 1
                    logger.info(f"Removed directory: {item}")
            except Exception as e:
                logger.warning(f"Failed to remove {item}: {e}")
        
        logger.info(f"Output cleanup completed: {files_removed}/{total_files} items removed from output/drawings")
            
    except Exception as e:
        logger.error(f"Error cleaning output/drawings folder: {e}")

# Add error handler for uncaught exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

# Add more robust startup
def start_flask_app():
    """Start Flask app with error handling"""
    try:
        logger.info("Starting Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        # Test that all critical functions work before starting
        logger.info("Running pre-flight checks...")
        
        # Test database access
        test_db_path = os.path.join(app.root_path, 'static', 'test.json')
        try:
            with open(test_db_path, 'w') as f:
                json.dump({"test": True}, f)
            os.remove(test_db_path)
            logger.info("Database write test passed")
        except Exception as e:
            logger.error(f"Database write test failed: {e}")
        
        # Test folder access
        try:
            test_file = os.path.join(MODELS_FOLDER, 'test.txt')
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            logger.info("Folder access test passed")
        except Exception as e:
            logger.error(f"Folder access test failed: {e}")
        
        logger.info("Pre-flight checks completed, starting server...")
        start_flask_app()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Critical error during startup: {e}", exc_info=True)
        input("Press Enter to exit...")  # Keep console open to see error
