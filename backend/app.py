from flask import Flask, jsonify, request, send_from_directory, url_for, make_response
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Configuration constants
class Config:
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'obj', 'gltf', 'glb', 'fbx'}
    ALLOWED_TEXTURE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tga', 'tiff'}
    MIME_TYPES = {
        'obj': 'application/octet-stream',
        'gltf': 'model/gltf+json',
        'glb': 'model/gltf-binary',
        'fbx': 'application/octet-stream',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'bmp': 'image/bmp',
        'tga': 'image/tga',
        'tiff': 'image/tiff'
    }

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Directory paths
MODELS_FOLDER = Path(app.root_path) / 'static' / 'models'
TEXTURES_FOLDER = Path(app.root_path) / 'static' / 'textures'
MODELS_DB_FILE = MODELS_FOLDER / 'models_db.json'
TEXTURES_DB_FILE = TEXTURES_FOLDER / 'textures_db.json'

# Ensure directories exist
MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
TEXTURES_FOLDER.mkdir(parents=True, exist_ok=True)

# Global storage
models: List[Dict] = []
textures: List[Dict] = []

def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def load_data_from_file(file_path: Path, data_type: str) -> List[Dict]:
    """Load data from JSON file with error handling"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} {data_type} from database")
                return data
        else:
            logger.info(f"No existing {data_type} database found")
            return []
    except Exception as e:
        logger.error(f"Error loading {data_type} database: {e}")
        return []

def save_data_to_file(data: List[Dict], file_path: Path, data_type: str) -> bool:
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} {data_type} to database")
        return True
    except Exception as e:
        logger.error(f"Error saving {data_type} database: {e}")
        return False

def create_file_entry(filename: str, original_name: str, file_stats: os.stat_result, 
                     entry_type: str, request_data: Dict) -> Dict:
    """Create a standardized file entry"""
    display_name = request_data.get("name", Path(original_name).stem)
    file_extension = Path(filename).suffix[1:].lower()
    
    base_entry = {
        "id": str(uuid.uuid4()),
        "name": display_name,
        "description": request_data.get("description", f"Uploaded {entry_type}"),
        "format": file_extension,
        "category": request_data.get("category", "uploaded"),
        "fileSize": file_stats.st_size,
        "createdAt": datetime.now().isoformat(),
    }
    
    if entry_type == "model":
        base_entry.update({
            "modelUrl": f"/models/{filename}",
            "isGenerated": False
        })
    else:  # texture
        base_entry.update({
            "textureUrl": f"/textures/{filename}",
            "type": request_data.get("type", "diffuse")
        })
    
    return base_entry

def scan_and_add_existing_files(folder_path: Path, extensions: set, 
                               existing_data: List[Dict], url_key: str) -> int:
    """Scan folder and add new files not in database"""
    if not folder_path.exists():
        return 0
    
    existing_filenames = {entry[url_key].split('/')[-1] for entry in existing_data if url_key in entry}
    added_count = 0
    
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix[1:].lower() in extensions:
            filename = file_path.name
            if filename not in existing_filenames:
                try:
                    file_stats = file_path.stat()
                    original_name = filename.split('_', 1)[1] if '_' in filename else filename
                    display_name = Path(original_name).stem
                    
                    entry_type = "model" if url_key == "modelUrl" else "texture"
                    new_entry = {
                        "id": str(uuid.uuid4()),
                        "name": display_name,
                        "description": f"{entry_type.title()} loaded from file: {original_name}",
                        "format": file_path.suffix[1:].lower(),
                        "category": "loaded",
                        "fileSize": file_stats.st_size,
                        "createdAt": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    }
                    
                    if entry_type == "model":
                        new_entry.update({
                            "modelUrl": f"/models/{filename}",
                            "isGenerated": False
                        })
                    else:
                        new_entry.update({
                            "textureUrl": f"/textures/{filename}",
                            "type": "diffuse"
                        })
                    
                    existing_data.append(new_entry)
                    added_count += 1
                    logger.info(f"Added existing {entry_type}: {display_name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to add {filename}: {e}")
    
    return added_count

def cleanup_missing_files() -> None:
    """Remove database entries for files that no longer exist"""
    global models, textures
    
    # Check models
    models[:] = [m for m in models if _file_exists_for_entry(m, "modelUrl", MODELS_FOLDER)]
    
    # Check textures  
    textures[:] = [t for t in textures if _file_exists_for_entry(t, "textureUrl", TEXTURES_FOLDER)]

def _file_exists_for_entry(entry: Dict, url_key: str, folder: Path) -> bool:
    """Check if file exists for database entry"""
    if url_key not in entry:
        return True  # Keep entries without URLs
    
    filename = entry[url_key].split('/')[-1]
    file_path = folder / filename
    exists = file_path.exists()
    
    if not exists:
        logger.info(f"Removing missing {url_key.replace('Url', '')}: {entry['name']}")
    
    return exists

def initialize_storage() -> None:
    """Initialize storage system"""
    global models, textures
    
    logger.info("Initializing storage system...")
    
    models = load_data_from_file(MODELS_DB_FILE, "models")
    textures = load_data_from_file(TEXTURES_DB_FILE, "textures")
    
    cleanup_missing_files()
    
    models_added = scan_and_add_existing_files(MODELS_FOLDER, Config.ALLOWED_EXTENSIONS, models, "modelUrl")
    textures_added = scan_and_add_existing_files(TEXTURES_FOLDER, Config.ALLOWED_TEXTURE_EXTENSIONS, textures, "textureUrl")
    
    if models_added:
        save_data_to_file(models, MODELS_DB_FILE, "models")
    if textures_added:
        save_data_to_file(textures, TEXTURES_DB_FILE, "textures")
    
    logger.info(f"Storage initialized: {len(models)} models, {len(textures)} textures")

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

# Initialize storage system
initialize_storage()

def _build_cors_preflight_response():
    """Build CORS preflight response"""
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response

def serve_file_with_mime(folder: Path, filename: str) -> any:
    """Serve file with proper MIME type and CORS headers"""
    try:
        extension = Path(filename).suffix[1:].lower()
        mime_type = Config.MIME_TYPES.get(extension, 'application/octet-stream')
        
        response = make_response(send_from_directory(str(folder), filename))
        response.headers['Content-Type'] = mime_type
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except FileNotFoundError:
        return jsonify({"error": f"File {filename} not found"}), 404
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/models', methods=['GET', 'OPTIONS'])
def get_models():
    """Returns list of all available 3D models"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
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
    
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not is_allowed_file(file.filename, Config.ALLOWED_EXTENSIONS):
            return jsonify({"error": f"File type not allowed. Supported: {', '.join(Config.ALLOWED_EXTENSIONS)}"}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = MODELS_FOLDER / unique_filename
        
        file.save(str(file_path))
        file_stats = file_path.stat()
        
        new_model = create_file_entry(unique_filename, filename, file_stats, "model", request.form.to_dict())
        models.append(new_model)
        save_data_to_file(models, MODELS_DB_FILE, "models")
        
        return jsonify(new_model), 201
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": "Upload failed"}), 500

@app.route('/models/<path:filename>')
def serve_model(filename):
    """Serves 3D model files"""
    return serve_file_with_mime(MODELS_FOLDER, filename)

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
        file_path = MODELS_FOLDER / filename
        if file_path.exists():
            os.remove(str(file_path))
    except Exception as e:
        logger.error(f"Error removing file: {e}")
    
    # Remove from models list
    models[:] = [m for m in models if m["id"] != model_id]
    save_data_to_file(models, MODELS_DB_FILE, "models")  # Save changes
    
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
    if not is_allowed_file(file.filename, Config.ALLOWED_TEXTURE_EXTENSIONS):
        return jsonify({"error": f"File type not allowed. Supported: {', '.join(Config.ALLOWED_TEXTURE_EXTENSIONS)}"}), 400
    
    # Secure filename and save file
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = TEXTURES_FOLDER / unique_filename
    file.save(str(file_path))
    
    # Get file stats
    file_stats = file_path.stat()
    
    new_texture = create_file_entry(unique_filename, filename, file_stats, "texture", request.form.to_dict())
    textures.append(new_texture)
    save_data_to_file(textures, TEXTURES_DB_FILE, "textures")  # Save to persistent storage
    return jsonify(new_texture), 201

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
        file_path = TEXTURES_FOLDER / filename
        if file_path.exists():
            os.remove(str(file_path))
    except Exception as e:
        logger.error(f"Error removing texture file: {e}")
    
    # Remove from textures list
    textures[:] = [t for t in textures if t["id"] != texture_id]
    save_data_to_file(textures, TEXTURES_DB_FILE, "textures")  # Save changes
    
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
            dest_mtl = str(dest_path).replace('.obj', '.mtl')
            
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
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = dest_path.stat()
            
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
            save_data_to_file(models, MODELS_DB_FILE, "models")
            
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
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = dest_path.stat()
            
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
            save_data_to_file(models, MODELS_DB_FILE, "models")
            
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
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            # Get file stats
            file_stats = dest_path.stat()
            
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
            save_data_to_file(models, MODELS_DB_FILE, "models")  # Save to persistent storage
            logger.info(f"Successfully created primitive: {new_model}")
            return jsonify({"success": True, "model": new_model}), 201
        else:
            logger.error(f"Primitive creation failed: {error}")
            return jsonify({"success": False, "error": error}), 500
            
    except Exception as e:
        logger.error(f"Exception in primitive drawing: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

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
