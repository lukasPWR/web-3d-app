"""
Blender drawing service for programmatic 3D model creation.
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime
import shutil
import os
import uuid
import logging
from pathlib import Path

from .blender_service import BlenderDrawingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Blender Drawing Service", version="1.0.0")

# Initialize Blender service
blender_service = BlenderDrawingService()

# Upload directory (ensure this exists)
UPLOAD_DIR = Path("./uploads/models")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory "database" for models (replace with real database in production)
models_db = {}
def save_models_db():
    """Save models database to file (JSON or other format)."""
    pass  # Implement database saving logic here

@app.post("/api/draw/session")
async def execute_drawing_session(session_data: dict):
    """Execute a complete drawing session with multiple commands."""
    try:
        success, output_path, error = blender_service.execute_drawing_session(session_data)
        
        if success:
            # Convert the generated model to our standard format
            # Generate model record
            model_id = str(uuid.uuid4())
            model_name = session_data.get('output_name', 'Generated Model')
            
            # Copy file to models directory
            output_filename = f"{model_id}.obj"
            final_path = UPLOAD_DIR / output_filename
            
            shutil.copy(output_path, final_path)
            
            # Create model record
            model_data = {
                "id": model_id,
                "name": model_name,
                "description": f"Programmatically generated model with {len(session_data.get('commands', []))} commands",
                "format": "obj",
                "modelUrl": f"/api/models/{model_id}/file",
                "createdAt": datetime.now().isoformat(),
                "fileSize": final_path.stat().st_size,
                "isGenerated": True
            }
            
            models_db[model_id] = model_data
            save_models_db()
            
            return {
                "success": True,
                "model": model_data,
                "session_id": session_data.get('session_id'),
                "message": "Model generated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail=f"Drawing failed: {error}")
            
    except Exception as e:
        logger.error(f"Drawing session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/draw/line")
async def draw_line(line_data: dict):
    """Draw a simple line."""
    try:
        points = line_data.get('points', [])
        color = line_data.get('color', '#ffffff')
        thickness = line_data.get('thickness', 0.01)
        name = line_data.get('name', 'Line')
        
        success, output_path, error = blender_service.create_line(points, color, thickness, name)
        
        if success:
            # Convert to model record (similar to session endpoint)
            model_id = str(uuid.uuid4())
            
            output_filename = f"{model_id}.obj"
            final_path = UPLOAD_DIR / output_filename
            
            shutil.copy(output_path, final_path)
            
            model_data = {
                "id": model_id,
                "name": name,
                "description": f"Generated line with {len(points)} points",
                "format": "obj",
                "modelUrl": f"/api/models/{model_id}/file",
                "createdAt": datetime.now().isoformat(),
                "fileSize": final_path.stat().st_size,
                "isGenerated": True
            }
            
            models_db[model_id] = model_data
            save_models_db()
            
            return {"success": True, "model": model_data}
        else:
            raise HTTPException(status_code=500, detail=f"Line drawing failed: {error}")
            
    except Exception as e:
        logger.error(f"Line drawing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/draw/primitive")
async def draw_primitive(primitive_data: dict):
    """Draw a primitive shape."""
    try:
        primitive_type = primitive_data.get('primitive_type', 'cube')
        location = primitive_data.get('location', [0, 0, 0])
        scale = primitive_data.get('scale', [1, 1, 1])
        color = primitive_data.get('color', '#8080ff')
        name = primitive_data.get('name', f'{primitive_type.title()}_Generated')
        
        success, output_path, error = blender_service.create_primitive(
            primitive_type, location, scale, color, name
        )
        
        if success:
            model_id = str(uuid.uuid4())
            
            output_filename = f"{model_id}.obj"
            final_path = UPLOAD_DIR / output_filename
            
            shutil.copy(output_path, final_path)
            
            model_data = {
                "id": model_id,
                "name": name,
                "description": f"Generated {primitive_type} primitive",
                "format": "obj",
                "modelUrl": f"/api/models/{model_id}/file",
                "createdAt": datetime.now().isoformat(),
                "fileSize": final_path.stat().st_size,
                "isGenerated": True
            }
            
            models_db[model_id] = model_data
            save_models_db()
            
            return {"success": True, "model": model_data}
        else:
            raise HTTPException(status_code=500, detail=f"Primitive drawing failed: {error}")
            
    except Exception as e:
        logger.error(f"Primitive drawing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
