from flask import Flask, jsonify, request, send_from_directory, make_response
import os
import uuid
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil
import logging
from pathlib import Path
from typing import List, Dict

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

MODELS_FOLDER = Path(app.root_path) / 'static' / 'models'
TEXTURES_FOLDER = Path(app.root_path) / 'static' / 'textures'
MODELS_DB_FILE = MODELS_FOLDER / 'models_db.json'
TEXTURES_DB_FILE = TEXTURES_FOLDER / 'textures_db.json'

MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
TEXTURES_FOLDER.mkdir(parents=True, exist_ok=True)

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
                        "format": file_path.suffix[1].lower(),
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
    
    models[:] = [m for m in models if _file_exists_for_entry(m, "modelUrl", MODELS_FOLDER)]
     
    textures[:] = [t for t in textures if _file_exists_for_entry(t, "textureUrl", TEXTURES_FOLDER)]

def _file_exists_for_entry(entry: Dict, url_key: str, folder: Path) -> bool:
    """Check if file exists for database entry"""
    if url_key not in entry:
        return True  
    
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

    MODELS_FOLDER.mkdir(parents=True, exist_ok=True)
    TEXTURES_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # Tworzenie pustych plików JSON jeśli nie istnieją
    if not MODELS_DB_FILE.exists():
        logger.info("Creating empty models database file")
        with open(MODELS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
    
    if not TEXTURES_DB_FILE.exists():
        logger.info("Creating empty textures database file")
        with open(TEXTURES_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
    
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
        
        file_path = folder / filename
        logger.info(f"Attempting to serve file: {file_path} (exists: {file_path.exists()})")
        
        response = make_response(send_from_directory(str(folder), filename))
        response.headers['Content-Type'] = mime_type
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except FileNotFoundError:
        logger.error(f"File not found when serving: {folder / filename}")
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

@app.route('/models/<path:filename>', methods=['GET', 'OPTIONS'])
def serve_model(filename):
    """Serves 3D model files with CORS support"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    logger.info(f"Serving model file: {filename}")
    
    file_path = MODELS_FOLDER / filename
    if not file_path.exists():
        logger.error(f"Model file not found: {file_path}")
        return jsonify({"error": f"File {filename} not found"}), 404
    
    return serve_file_with_mime(MODELS_FOLDER, filename)

@app.route('/textures/<path:filename>', methods=['GET', 'OPTIONS'])
def serve_texture(filename):
    """Serves texture files with CORS support"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    return serve_file_with_mime(TEXTURES_FOLDER, filename)

@app.route('/api/models/<model_id>', methods=['DELETE', 'OPTIONS'])
def delete_model(model_id):
    """Deletes a 3D model"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    model = next((model for model in models if model["id"] == model_id), None)
    if not model:
        return jsonify({"error": "Model not found"}), 404
    
    try:
        filename = model["modelUrl"].split("/")[-1]
        file_path = MODELS_FOLDER / filename
        if file_path.exists():
            os.remove(str(file_path))
    except Exception as e:
        logger.error(f"Error removing file: {e}")
    
    models[:] = [m for m in models if m["id"] != model_id]
    save_data_to_file(models, MODELS_DB_FILE, "models")  
    
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
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not is_allowed_file(file.filename, Config.ALLOWED_TEXTURE_EXTENSIONS):
        return jsonify({"error": f"File type not allowed. Supported: {', '.join(Config.ALLOWED_TEXTURE_EXTENSIONS)}"}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = TEXTURES_FOLDER / unique_filename
    file.save(str(file_path))
    
    file_stats = file_path.stat()
    
    new_texture = create_file_entry(unique_filename, filename, file_stats, "texture", request.form.to_dict())
    textures.append(new_texture)
    save_data_to_file(textures, TEXTURES_DB_FILE, "textures")  
    return jsonify(new_texture), 201

@app.route('/api/textures/<texture_id>', methods=['DELETE', 'OPTIONS'])
def delete_texture(texture_id):
    """Deletes a texture"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    texture = next((texture for texture in textures if texture["id"] == texture_id), None)
    if not texture:
        return jsonify({"error": "Texture not found"}), 404
    
    try:
        filename = texture["textureUrl"].split("/")[-1]
        file_path = TEXTURES_FOLDER / filename
        if file_path.exists():
            os.remove(str(file_path))
    except Exception as e:
        logger.error(f"Error removing texture file: {e}")
    
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
        shutil.copy2(output_path, dest_path)
        
        if output_path.endswith('.obj'):
            source_mtl = output_path.replace('.obj', '.mtl')
            dest_mtl = str(dest_path).replace('.obj', '.mtl')
            
            if os.path.exists(source_mtl):
                try:
                    with open(source_mtl, 'r') as f:
                        mtl_content = f.read().strip()
                    
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
            
            file_stats = dest_path.stat()
            
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
            filename = os.path.basename(output_path)
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            file_stats = dest_path.stat()
            
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
            filename = os.path.basename(output_path)
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            file_stats = dest_path.stat()
            
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
            save_data_to_file(models, MODELS_DB_FILE, "models") 
            logger.info(f"Successfully created primitive: {new_model}")
            return jsonify({"success": True, "model": new_model}), 201
        else:
            logger.error(f"Primitive creation failed: {error}")
            return jsonify({"success": False, "error": error}), 500
            
    except Exception as e:
        logger.error(f"Exception in primitive drawing: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/draw/custom-coords', methods=['POST', 'OPTIONS'])
def draw_custom_coords_endpoint():
    """Create a custom mesh from coordinate text input"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if not blender_service:
        return jsonify({"success": False, "error": "Blender service not available"}), 503
    
    try:
        data = request.get_json()
        logger.info(f"Received custom coordinates request: {json.dumps(data, indent=2)}")
        
        coordinates_text = data.get('coordinates_text', '')
        color = data.get('color', '#cccccc')
        name = data.get('name', 'CustomMesh')
        use_convex_hull = data.get('use_convex_hull', True)
        
        if isinstance(coordinates_text, list):
            # Frontend sent points as list of objects [{x, y, z}, ...]
            points = coordinates_text
            coordinates_text_str = '\n'.join([f"{float(p.get('x', 0))} {float(p.get('y', 0))} {float(p.get('z', 0))}" for p in points])
            logger.info(f"Converted {len(points)} points from array to text format")
        elif isinstance(coordinates_text, str):
            coordinates_text_str = coordinates_text.strip()
            if not coordinates_text_str:
                return jsonify({"error": "Coordinates text is required"}), 400
        else:
            return jsonify({"error": "Invalid coordinates format"}), 400
        
        logger.info(f"Final coordinates text:\n{coordinates_text_str}")
        
        lines = [line.strip() for line in coordinates_text_str.split('\n') if line.strip()]
        if len(lines) < 3:
            return jsonify({"error": f"At least 3 coordinate points are required, got {len(lines)}"}), 400
        
        parsed_points = []
        for i, line in enumerate(lines):
            parts = line.split()
            if len(parts) != 3:
                return jsonify({"error": f"Invalid coordinate format at line {i+1}: '{line}'. Expected 'X Y Z'"}), 400
            try:
                x, y, z = [float(x) for x in parts]
                parsed_points.append((x, y, z))
            except ValueError:
                return jsonify({"error": f"Invalid numeric values at line {i+1}: '{line}'"}), 400
        
        logger.info(f"Successfully parsed {len(parsed_points)} coordinate points:")
        for i, (x, y, z) in enumerate(parsed_points):
            logger.info(f"  Point {i+1}: ({x}, {y}, {z})")
        
        logger.info(f"Creating custom mesh with convex_hull={use_convex_hull}")
        
        color_obj = blender_service._convert_hex_to_rgba(color)
        
        session_data = {
            "session_id": str(uuid.uuid4()),
            "clear_scene": True,
            "commands": [
                ("custom_coords", {
                    "coordinates_text": coordinates_text_str,
                    "color": color_obj,
                    "name": name,
                    "use_convex_hull": use_convex_hull
                })
            ],
            "output_format": "obj",
            "output_name": f"custom_mesh_{name.lower().replace(' ', '_')}"
        }
        
        logger.info(f"Session data created: {json.dumps(session_data, indent=2)}")
        
        success, output_path, error = blender_service.execute_drawing_session(session_data)
        
        logger.info(f"Blender service result: success={success}, output_path={output_path}, error={error}")
        
        if success and output_path:
            if not os.path.exists(output_path):
                logger.error(f"Output file does not exist: {output_path}")
                return jsonify({"success": False, "error": "Generated file not found"}), 500
            
            output_size = os.path.getsize(output_path)
            logger.info(f"Generated file size: {output_size} bytes")
            
            if output_size < 100:
                logger.warning(f"Generated file is very small ({output_size} bytes), reading content for debug:")
                try:
                    with open(output_path, 'r') as f:
                        content = f.read()
                    logger.warning(f"File content preview:\n{content}")
                except Exception as e:
                    logger.error(f"Failed to read generated file: {e}")
            
            filename = os.path.basename(output_path)
            dest_path = MODELS_FOLDER / filename
            cleanup_generated_files(output_path, dest_path)
            
            file_stats = dest_path.stat()
            logger.info(f"Copied file size: {file_stats.st_size} bytes")
            
            new_model = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": f"Custom mesh from coordinates ({len(lines)} vertices, convex_hull={use_convex_hull})",
                "modelUrl": f"/models/{filename}",
                "format": "obj",
                "category": "generated",
                "fileSize": file_stats.st_size,
                "createdAt": datetime.now().isoformat(),
                "isGenerated": True
            }
            
            models.append(new_model)
            save_data_to_file(models, MODELS_DB_FILE, "models")
            
            logger.info(f"Successfully created custom mesh model: {new_model}")
            return jsonify({"success": True, "model": new_model}), 201
        else:
            logger.error(f"Custom mesh creation failed: {error}")
            return jsonify({"success": False, "error": error or "Failed to create custom mesh"}), 500
            
    except Exception as e:
        logger.error(f"Exception in custom mesh creation: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/models/<model_id>/update', methods=['POST', 'OPTIONS'])
def update_model(model_id):
    """Updates a 3D model with new transforms and material properties"""
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if 'blender_service' not in globals():
            return jsonify({"error": "Blender service not available"}), 500
        
        model = next((model for model in models if model["id"] == model_id), None)
        if not model:
            return jsonify({"error": "Model not found"}), 404
        
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "No update data provided"}), 400
        
        logger.info(f"Updating model {model_id} with data: {json.dumps(update_data, indent=2)}")
        
        original_filename = model["modelUrl"].split("/")[-1]
        original_path = MODELS_FOLDER / original_filename
        
        if not original_path.exists():
            return jsonify({"error": "Original model file not found"}), 404
        
        blender_update_spec = {}
        
        if "position" in update_data:
            blender_update_spec["location"] = update_data["position"]
        
        if "rotation" in update_data:
            blender_update_spec["rotation"] = update_data["rotation"]
          
        if "scale" in update_data:
            blender_update_spec["scale"] = update_data["scale"]
        
        if "material" in update_data:
            material_spec = {}
            mat_data = update_data["material"]
            
            if "color" in mat_data:
                color_hex = mat_data["color"]
                if color_hex.startswith('#'):
                    color_hex = color_hex[1:]
                r = int(color_hex[0:2], 16) / 255.0
                g = int(color_hex[2:4], 16) / 255.0
                b = int(color_hex[4:6], 16) / 255.0
                material_spec["color"] = [r, g, b, 1.0]
            
            if "roughness" in mat_data:
                material_spec["roughness"] = float(mat_data["roughness"])
            
            if "metalness" in mat_data:
                material_spec["metallic"] = float(mat_data["metalness"])
            
            if "emissive" in mat_data:
                emissive_hex = mat_data["emissive"]
                if emissive_hex.startswith('#'):
                    emissive_hex = emissive_hex[1:]
                r = int(emissive_hex[0:2], 16) / 255.0
                g = int(emissive_hex[2:4], 16) / 255.0
                b = int(emissive_hex[4:6], 16) / 255.0
                material_spec["emission"] = [r, g, b]
            
            if "emissiveIntensity" in mat_data:
                material_spec["emissiveIntensity"] = float(mat_data["emissiveIntensity"])
            
            if "textureId" in mat_data and mat_data["textureId"]:
                material_spec["textureId"] = str(mat_data["textureId"])
                logger.info(f"Adding texture ID to material spec: {mat_data['textureId']}")
            
            if "textureScale" in mat_data:
                material_spec["textureScale"] = float(mat_data["textureScale"])
                logger.info(f"Adding texture scale to material spec: {mat_data['textureScale']}")
            
            if material_spec:
                blender_update_spec["material"] = material_spec
        
        model_name = model.get("name", "updated_model")
        safe_name = "".join(c for c in model_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        output_name = f"{safe_name}_edited"
        
        logger.info(f"Blender update spec: {json.dumps(blender_update_spec, indent=2)}")
        
        success, updated_model_path, error = blender_service.update_model(
            str(original_path), 
            blender_update_spec,
            output_name
        )
        
        if not success:
            logger.error(f"Failed to update model: {error}")
            return jsonify({"error": f"Failed to update model: {error}"}), 500
        
        output_filename = f"{model_id}_edited.obj"
        static_output_path = MODELS_FOLDER / output_filename
        
        try:
            shutil.copy2(updated_model_path, static_output_path)
            
            mtl_source = updated_model_path.replace('.obj', '.mtl')
            if os.path.exists(mtl_source):
                mtl_output_path = static_output_path.with_suffix('.mtl')
                shutil.copy2(mtl_source, mtl_output_path)
                logger.info(f"Copied MTL file to: {mtl_output_path}")
                
                try:
                    with open(mtl_source, 'r') as f:
                        mtl_content = f.read()
                    
                    import re
                    texture_references = re.findall(r'map_\w+\s+(\S+)', mtl_content)
                    
                    for texture_ref in texture_references:
                        texture_source = os.path.join(os.path.dirname(mtl_source), texture_ref)
                        if os.path.exists(texture_source):
                            texture_dest = MODELS_FOLDER / texture_ref
                            if not texture_dest.exists():
                                shutil.copy2(texture_source, texture_dest)
                                logger.info(f"Copied texture file: {texture_ref}")
                        else:
                            logger.warning(f"Texture file not found: {texture_source}")
                            
                except Exception as texture_error:
                    logger.warning(f"Error copying texture files: {texture_error}")
            
            new_model = {
                "id": str(uuid.uuid4()),
                "name": f"{model['name']} (Edited)",
                "description": f"Edited version of {model['name']}",
                "format": "obj",
                "category": "edited",
                "fileSize": os.path.getsize(static_output_path),
                "createdAt": datetime.now().isoformat(),
                "modelUrl": f"/models/{output_filename}",
                "thumbnailUrl": None,
                "tags": model.get("tags", []) + ["edited"],
                "isEdited": True,
                "originalModelId": model_id
            }
            
            models.append(new_model)
            save_data_to_file(models, MODELS_DB_FILE, "models")
            
            logger.info(f"Saved {len(models)} models to database")
            
            return jsonify({
                "success": True,
                "message": "Model updated successfully",
                "updatedModel": new_model
            })
            
        except Exception as copy_error:
            logger.error(f"Failed to copy updated model: {copy_error}")
            return jsonify({"error": f"Failed to save updated model: {str(copy_error)}"}), 500
        
    except Exception as e:
        logger.error(f"Error updating model: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to update model: {str(e)}"}), 500

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


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

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
