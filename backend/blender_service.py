"""
Service for executing Blender drawing commands in headless mode.
"""

import subprocess
import json
import uuid
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

class BlenderDrawingService:
    """Service for executing Blender drawing operations."""
    
    def __init__(self, blender_executable: str = r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"):
        self.blender_executable = blender_executable
        self.timeout = 300  # 5 minutes
    
    def _create_execution_script(self, session_file: str, result_file: str) -> str:
        """Create Python script for Blender execution."""
        # Use repr() to properly escape paths for Python strings
        session_file_repr = repr(session_file)
        result_file_repr = repr(result_file)
        
        return f'''
import sys
import json
import os
from pathlib import Path
import traceback

# Enable all logging
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting Blender execution script")

# Find backend directory containing blender_draw module
backend_candidates = [
    Path(os.getcwd()),
    Path(os.getcwd()) / "backend",
    Path(__file__).parent.parent,
    Path(__file__).parent.parent / "backend"
]

backend_dir = None
for candidate in backend_candidates:
    logger.debug(f"Checking backend candidate: {{candidate}}")
    if (candidate / "blender_draw").exists():
        backend_dir = candidate
        logger.info(f"Found backend directory: {{backend_dir}}")
        break

if not backend_dir:
    error_msg = f"Could not find blender_draw module in candidates: {{[str(c) for c in backend_candidates]}}"
    logger.error(error_msg)
    raise ImportError(error_msg)

sys.path.insert(0, str(backend_dir))
logger.info(f"Added to Python path: {{str(backend_dir)}}")

try:
    logger.info("Importing blender_draw.draw_models")
    from blender_draw.draw_models import execute_drawing_session
    
    logger.info(f"Reading session data from: {session_file_repr}")
    with open({session_file_repr}, "r") as f:
        session_data = json.load(f)
    
    logger.info(f"Session data loaded: {{json.dumps(session_data, indent=2)}}")
    
    logger.info("Executing drawing session...")
    session_id, output_path = execute_drawing_session(session_data)
    logger.info(f"Drawing session completed: session_id={{session_id}}, output_path={{output_path}}")
    
    # Verify output file exists
    if output_path and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        logger.info(f"Output file exists with size: {{file_size}} bytes")
        
        # Read and log file content preview for debugging
        if file_size < 1000:  # Only for small files
            try:
                with open(output_path, 'r') as f:
                    content = f.read()
                logger.info(f"File content preview:\\n{{content[:500]}}")
            except Exception as e:
                logger.warning(f"Could not read file content: {{e}}")
    else:
        logger.error(f"Output file does not exist: {{output_path}}")
    
    result = {{
        "success": True,
        "session_id": session_id,
        "output_path": str(output_path),
        "error": None
    }}
    
except Exception as e:
    error_msg = str(e)
    tb = traceback.format_exc()
    logger.error(f"Exception occurred: {{error_msg}}")
    logger.error(f"Traceback:\\n{{tb}}")
    
    result = {{
        "success": False,
        "session_id": None,
        "output_path": None,
        "error": error_msg,
        "traceback": tb
    }}

logger.info(f"Writing result to: {result_file_repr}")
with open({result_file_repr}, "w") as f:
    json.dump(result, f, indent=2)

logger.info("Blender execution script completed")
'''
    
    def execute_drawing_session(self, session_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Execute a drawing session in headless Blender."""
        if "session_id" not in session_data:
            session_data["session_id"] = str(uuid.uuid4())
        
        print(f"Executing drawing session with data: {json.dumps(session_data, indent=2)}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create session and result files
            session_file = temp_path / "session.json"
            result_file = temp_path / "result.json"
            script_file = temp_path / "execute_drawing.py"
            
            # Write files
            with open(session_file, "w") as f:
                json.dump(session_data, f, default=str, indent=2)
            
            print(f"Session file written to: {session_file}")
            print(f"Session data contents: {json.dumps(session_data, indent=2)}")
            
            script_content = self._create_execution_script(str(session_file), str(result_file))
            with open(script_file, "w", encoding='utf-8') as f:
                f.write(script_content)
            
            return self._execute_blender_command(script_file, result_file)
    
    def _execute_blender_command(self, script_file: Path, result_file: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Execute Blender command and return results."""
        try:
            cmd = [
                self.blender_executable,
                "--background",
                "--python", str(script_file)
            ]
            
            print(f"Executing Blender command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                cwd=str(Path(__file__).parent)
            )
            
            print(f"Blender stdout: {result.stdout}")
            if result.stderr:
                print(f"Blender stderr: {result.stderr}")
            print(f"Blender return code: {result.returncode}")
            
            if result_file.exists():
                with open(result_file, "r") as f:
                    execution_result = json.load(f)
                
                print(f"Execution result: {json.dumps(execution_result, indent=2)}")
                
                if execution_result["success"]:
                    return True, execution_result["output_path"], None
                else:
                    error_details = execution_result.get("error", "Unknown error")
                    if execution_result.get("traceback"):
                        error_details += f"\n\nTraceback:\n{execution_result['traceback']}"
                    return False, None, error_details
            else:
                return False, None, f"Blender execution failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, None, "Blender execution timed out"
        except Exception as e:
            return False, None, f"Execution error: {str(e)}"
    
    def _convert_hex_to_rgba(self, hex_color: str) -> Dict[str, float]:
        """Convert hex color to RGBA dictionary."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'FF'
        
        return {
            "r": int(hex_color[0:2], 16) / 255.0,
            "g": int(hex_color[2:4], 16) / 255.0,
            "b": int(hex_color[4:6], 16) / 255.0,
            "a": int(hex_color[6:8], 16) / 255.0
        }
    
    def create_line(self, points: list, color: str = "#ffffff", 
                   thickness: float = 0.01, name: str = "Line") -> Tuple[bool, Optional[str], Optional[str]]:
        """Create a simple line drawing."""
        point_objects = [{"x": p[0], "y": p[1], "z": p[2]} for p in points]
        color_obj = self._convert_hex_to_rgba(color)
        
        session_data = {
            "session_id": str(uuid.uuid4()),
            "clear_scene": True,
            "commands": [
                ("line", {
                    "points": point_objects,
                    "color": color_obj,
                    "thickness": thickness,
                    "name": name
                })
            ],
            "output_format": "obj",
            "output_name": "line_drawing"
        }
        
        return self.execute_drawing_session(session_data)
    
    def create_primitive(self, primitive_type: str, location: list = [0, 0, 0],
                        scale: list = [1, 1, 1], color: str = "#8080ff",
                        name: str = "Primitive") -> Tuple[bool, Optional[str], Optional[str]]:
        """Create a primitive shape."""
        color_obj = self._convert_hex_to_rgba(color)
        
        session_data = {
            "session_id": str(uuid.uuid4()),
            "clear_scene": True,
            "commands": [
                ("primitive", {
                    "primitive_type": primitive_type,
                    "location": {"x": location[0], "y": location[1], "z": location[2]},
                    "scale": {"x": scale[0], "y": scale[1], "z": scale[2]},
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "color": color_obj,
                    "name": name
                })
            ],
            "output_format": "obj",
            "output_name": "primitive_drawing"
        }
        
        return self.execute_drawing_session(session_data)
    
    def create_custom_mesh_from_coords(self, coordinates_text: str, color: str = "#cccccc", 
                                     name: str = "CustomMesh", use_convex_hull: bool = True) -> Tuple[bool, Optional[str], Optional[str]]:
        """Create a custom mesh from text coordinates."""
        try:
            # Validate and parse coordinates
            lines = [line.strip() for line in coordinates_text.split('\n') if line.strip()]
            if len(lines) < 3:
                return False, None, f"At least 3 coordinate points required, got {len(lines)}"
            
            # Validate coordinate format
            parsed_points = []
            for i, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 3:
                    return False, None, f"Invalid coordinate format at line {i+1}: '{line}'"
                try:
                    x, y, z = [float(p) for p in parts]
                    parsed_points.append({"x": x, "y": y, "z": z})
                except ValueError:
                    return False, None, f"Invalid numeric values at line {i+1}: '{line}'"
            
            color_obj = self._convert_hex_to_rgba(color)
            
            session_data = {
                "session_id": str(uuid.uuid4()),
                "clear_scene": True,
                "commands": [
                    ("custom_coords", {
                        "coordinates_text": coordinates_text,
                        "coordinates_points": parsed_points,  # Also send parsed points
                        "color": color_obj,
                        "name": name,
                        "use_convex_hull": use_convex_hull
                    })
                ],
                "output_format": "obj",
                "output_name": f"custom_mesh_{name.lower().replace(' ', '_')}"
            }
            
            return self.execute_drawing_session(session_data)
            
        except Exception as e:
            return False, None, f"Error processing coordinates: {str(e)}"
    
    def update_model(self, original_obj_path: str, updates: Dict[str, Any], output_name: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Update an existing OBJ model with new transforms and material properties.
        
        Args:
            original_obj_path: Path to the original .obj file
            updates: Dictionary with update specifications
            output_name: Optional name for output file
            
        Returns:
            Tuple of (success, output_path, error_message)
        """
        try:
            import tempfile
            from pathlib import Path
            import math
            
            # Validate original file exists
            if not os.path.exists(original_obj_path):
                return False, None, f"Original OBJ file not found: {original_obj_path}"
            
            # Generate output name if not provided
            if not output_name:
                original_name = Path(original_obj_path).stem
                timestamp = str(uuid.uuid4())[:8]
                output_name = f"{original_name}_edited_{timestamp}"
            
            # Prepare output directory
            output_dir = Path(__file__).parent / "output" / "drawings"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{output_name}.obj"
            
            # Create temp directory for script execution
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create update specification file
                update_file = temp_path / "update_spec.json"
                script_file = temp_path / "update_script.py"
                result_file = temp_path / "result.json"
                
                # Prepare the update specification with object name
                obj_name = Path(original_obj_path).stem
                
                # Convert updates dictionary to Blender-compatible format
                blender_updates = {"object": obj_name}
                
                # Handle position/location - support both array and object formats
                if "position" in updates:
                    pos = updates["position"]
                    if isinstance(pos, list) and len(pos) >= 3:
                        blender_updates["location"] = [float(pos[0]), float(pos[1]), float(pos[2])]
                    elif isinstance(pos, dict):
                        blender_updates["location"] = [
                            float(pos.get("x", 0)), 
                            float(pos.get("y", 0)), 
                            float(pos.get("z", 0))
                        ]
                elif "location" in updates:
                    loc = updates["location"]
                    if isinstance(loc, list) and len(loc) >= 3:
                        blender_updates["location"] = [float(loc[0]), float(loc[1]), float(loc[2])]
                    elif isinstance(loc, dict):
                        blender_updates["location"] = [
                            float(loc.get("x", 0)), 
                            float(loc.get("y", 0)), 
                            float(loc.get("z", 0))
                        ]
                
                # Handle rotation - support both array and object formats, convert to radians
                if "rotation" in updates:
                    rot = updates["rotation"]
                    if isinstance(rot, list) and len(rot) >= 3:
                        blender_updates["rotation"] = [
                            math.radians(float(rot[0])),
                            math.radians(float(rot[1])),
                            math.radians(float(rot[2]))
                        ]
                    elif isinstance(rot, dict):
                        blender_updates["rotation"] = [
                            math.radians(float(rot.get("x", 0))),
                            math.radians(float(rot.get("y", 0))),
                            math.radians(float(rot.get("z", 0)))
                        ]
                
                # Handle scale - support both array and object formats
                if "scale" in updates:
                    scale = updates["scale"]
                    if isinstance(scale, list) and len(scale) >= 3:
                        blender_updates["scale"] = [float(scale[0]), float(scale[1]), float(scale[2])]
                    elif isinstance(scale, dict):
                        blender_updates["scale"] = [
                            float(scale.get("x", 1)), 
                            float(scale.get("y", 1)), 
                            float(scale.get("z", 1))
                        ]
                
                # Handle material properties
                if "material" in updates:
                    mat = updates["material"]
                    material_spec = {}
                    
                    if "color" in mat:
                        color = mat["color"]
                        if isinstance(color, str):  # Handle hex color format
                            color_obj = self._convert_hex_to_rgba(color)
                            material_spec["color"] = [color_obj["r"], color_obj["g"], color_obj["b"], color_obj["a"]]
                        elif isinstance(color, list) and len(color) >= 3:  # Handle array format
                            material_spec["color"] = [
                                float(color[0]), 
                                float(color[1]), 
                                float(color[2]), 
                                float(color[3]) if len(color) > 3 else 1.0
                            ]
                    
                    if "roughness" in mat:
                        material_spec["roughness"] = float(mat["roughness"])
                        
                    # Handle both "metallic" and "metalness"
                    if "metallic" in mat:
                        material_spec["metallic"] = float(mat["metallic"])
                    elif "metalness" in mat:
                        material_spec["metallic"] = float(mat["metalness"])
                    
                    # Handle emission/emissive
                    emission_color = None
                    if "emission" in mat:
                        emission = mat["emission"]
                        if isinstance(emission, str):  # Handle hex format
                            emission_obj = self._convert_hex_to_rgba(emission)
                            emission_color = [emission_obj["r"], emission_obj["g"], emission_obj["b"]]
                        elif isinstance(emission, list) and len(emission) >= 3:  # Handle array format
                            emission_color = [float(emission[0]), float(emission[1]), float(emission[2])]
                    elif "emissive" in mat:
                        emissive = mat["emissive"]
                        if isinstance(emissive, str):  # Handle hex format
                            emissive_obj = self._convert_hex_to_rgba(emissive)
                            emission_color = [emissive_obj["r"], emissive_obj["g"], emissive_obj["b"]]
                        elif isinstance(emissive, list) and len(emissive) >= 3:  # Handle array format
                            emission_color = [float(emissive[0]), float(emissive[1]), float(emissive[2])]
                    
                    if emission_color:
                        material_spec["emission"] = emission_color
                    
                    if "emissiveIntensity" in mat:
                        material_spec["emissiveIntensity"] = float(mat["emissiveIntensity"])
                    
                    # NEW: Handle texture information
                    if "textureId" in mat and mat["textureId"]:
                        material_spec["textureId"] = str(mat["textureId"])
                        
                    if "textureScale" in mat:
                        material_spec["textureScale"] = float(mat["textureScale"])
                    
                    if material_spec:
                        blender_updates["material"] = material_spec
                
                # Write update specification to file
                with open(update_file, "w") as f:
                    json.dump(blender_updates, f, indent=2)
                
                print(f"Blender update spec: {json.dumps(blender_updates, indent=2)}")
                
                # Create Blender script for updating
                script_content = self._create_update_script(
                    str(update_file), 
                    original_obj_path, 
                    str(output_path)
                )
                
                with open(script_file, "w", encoding='utf-8') as f:
                    f.write(script_content)
                
                # Execute Blender command
                cmd = [
                    self.blender_executable,
                    "--background",
                    "--python", str(script_file),
                    "--", 
                    "--input", str(update_file),
                    "--obj", original_obj_path,
                    "--output", str(output_path)
                ]
                
                print(f"Executing Blender update command: {' '.join(cmd)}")
                
                try:
                    result = subprocess.run(
                        cmd, 
                        capture_output=True, 
                        text=True, 
                        timeout=self.timeout,
                        cwd=str(Path(__file__).parent)
                    )
                    
                    print(f"Blender update stdout: {result.stdout}")
                    if result.stderr:
                        print(f"Blender update stderr: {result.stderr}")
                    
                    if result.returncode != 0:
                        return False, None, f"Blender update failed with code {result.returncode}: {result.stderr}"
                    
                    # Check if output file was created
                    if output_path.exists():
                        print(f"✓ Output file created at: {output_path}")
                        print(f"✓ Output file size: {output_path.stat().st_size} bytes")
                        
                        # Read and log a few lines of the created file for debugging
                        try:
                            with open(output_path, 'r') as f:
                                lines = f.readlines()[:15]  # First 15 lines
                            print("✓ Output file content preview:")
                            for i, line in enumerate(lines):
                                print(f"  {i+1}: {line.rstrip()}")
                        except Exception as e:
                            print(f"✗ Could not read output file: {e}")
                        
                        return True, str(output_path), None
                    else:
                        return False, None, "Output file was not created"
                        
                except subprocess.TimeoutExpired:
                    return False, None, "Blender update timed out"
                except Exception as e:
                    return False, None, f"Execution error: {str(e)}"
                    
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return False, None, f"Error updating model: {str(e)}\n{tb}"
    
    def _create_update_script(self, update_file: str, obj_path: str, output_path: str) -> str:
        """Create Python script for Blender model update execution."""
        return f'''
import bpy
import sys
import json
import os
import math
from pathlib import Path
import logging
from mathutils import Vector, Euler, Matrix
import bmesh

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting Blender model update script")

def parse_args():
    """Parse command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(description="Update object transforms & material")
    parser.add_argument("--input", type=str, required=True, help="Path to JSON file with update spec")
    parser.add_argument("--obj", type=str, required=True, help="Path to OBJ file to update")
    parser.add_argument("--output", type=str, required=True, help="Path to save updated OBJ")
    return parser.parse_args(sys.argv[sys.argv.index("--")+1:])

def load_obj(filepath):
    """Import OBJ file using Blender 4.4+ API"""
    logger.info(f"Importing OBJ: {{filepath}}")
    # First clear any existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import OBJ file using new Blender 4.4+ operator
    bpy.ops.wm.obj_import(filepath=filepath)
    
    # Return the imported object
    if len(bpy.context.selected_objects) > 0:
        obj = bpy.context.selected_objects[0]
        logger.info(f"Imported object: {{obj.name}}")
        
        # Set object as active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Log original vertex positions
        logger.info("Original imported vertex positions:")
        for i, vert in enumerate(obj.data.vertices[:8]):
            logger.info(f"  Original Vertex {{i}}: {{vert.co[0]:.6f}}, {{vert.co[1]:.6f}}, {{vert.co[2]:.6f}}")
        
        return obj
    else:
        logger.error("No objects were imported")
        return None

def apply_updates(obj, spec):
    """Apply updates to object using direct mesh vertex manipulation"""
    logger.info(f"Applying updates to object: {{obj.name}}")
    
    # Make sure object is selected and active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Reset object transforms to ensure clean state
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    obj.rotation_mode = 'XYZ'
    
    # Force update
    bpy.context.view_layer.update()
    
    # Apply transformations directly to mesh vertices
    if any(key in spec for key in ["location", "rotation", "scale"]):
        logger.info("Applying transformations directly to mesh vertices...")
        
        # Get mesh data
        mesh = obj.data
        
        # Create transformation matrices
        scale_matrix = Matrix.Identity(4)
        rotation_matrix = Matrix.Identity(4)
        translation_matrix = Matrix.Identity(4)
        
        # Build scale matrix
        if "scale" in spec:
            scale = spec["scale"]
            scale_matrix = Matrix.Scale(scale[0], 4, (1, 0, 0)) @ Matrix.Scale(scale[1], 4, (0, 1, 0)) @ Matrix.Scale(scale[2], 4, (0, 0, 1))
            logger.info(f"Scale matrix: {{scale}}")
        
        # Build rotation matrix
        if "rotation" in spec:
            rotation = spec["rotation"]
            # Apply rotations in correct order: Z, Y, X (Euler XYZ)
            euler = Euler((rotation[0], rotation[1], rotation[2]), 'XYZ')
            rotation_matrix = euler.to_matrix().to_4x4()
            logger.info(f"Rotation: {{[math.degrees(r) for r in rotation]}} degrees")
        
        # Build translation matrix
        if "location" in spec:
            location = spec["location"]
            translation_matrix = Matrix.Translation((location[0], location[1], location[2]))
            logger.info(f"Translation: {{location}}")
        
        # FIXED: Combine transformations in correct order: Scale -> Rotate -> Translate
        # But apply them in reverse order to the vertex positions
        transform_matrix = translation_matrix @ rotation_matrix @ scale_matrix
        
        logger.info("Applying transformations step by step to vertices...")
        
        # Apply transformations step by step for better control
        temp_vertices = []
        
        # First collect all vertex positions
        for vert in mesh.vertices:
            temp_vertices.append(Vector((vert.co.x, vert.co.y, vert.co.z)))
        
        # Apply scale first
        if "scale" in spec:
            scale = spec["scale"]
            for i, vert_co in enumerate(temp_vertices):
                temp_vertices[i] = Vector((
                    vert_co.x * scale[0],
                    vert_co.y * scale[1], 
                    vert_co.z * scale[2]
                ))
            logger.info(f"Applied scale: {{scale}}")
        
        # Apply rotation second
        if "rotation" in spec:
            rotation = spec["rotation"]
            # Create rotation matrix
            rot_x = Matrix.Rotation(rotation[0], 3, 'X').to_4x4()
            rot_y = Matrix.Rotation(rotation[1], 3, 'Y').to_4x4()
            rot_z = Matrix.Rotation(rotation[2], 3, 'Z').to_4x4()
            
            # Apply rotations in order: X, then Y, then Z
            combined_rotation = rot_z @ rot_y @ rot_x
            
            for i, vert_co in enumerate(temp_vertices):
                vert_co_4d = Vector((vert_co.x, vert_co.y, vert_co.z, 1.0))
                rotated = combined_rotation @ vert_co_4d
                temp_vertices[i] = Vector((rotated.x, rotated.y, rotated.z))
            logger.info(f"Applied rotation: {{[math.degrees(r) for r in rotation]}} degrees")
        
        # Apply translation last
        if "location" in spec:
            location = spec["location"]
            for i, vert_co in enumerate(temp_vertices):
                temp_vertices[i] = Vector((
                    vert_co.x + location[0],
                    vert_co.y + location[1],
                    vert_co.z + location[2]
                ))
            logger.info(f"Applied translation: {{location}}")
        
        # Now update the actual mesh vertices
        for i, vert in enumerate(mesh.vertices):
            vert.co = temp_vertices[i]
    
    # Handle material updates
    if "material" in spec:
        logger.info("Applying material updates...")
        
        # Get or create material
        if obj.data.materials:
            mat = obj.data.materials[0]
        else:
            mat = bpy.data.materials.new(name=f"{{obj.name}}_material")
            obj.data.materials.append(mat)
        
        # Enable nodes for material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create Principled BSDF
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # Create Material Output
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        
        # Link BSDF to output
        links.new(bsdf.outputs['BSDF'], material_output.inputs['Surface'])
        
        material_spec = spec["material"]
        
        # Apply color
        if "color" in material_spec:
            color = material_spec["color"]
            bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], color[3])
            # Also set legacy diffuse color for OBJ export
            mat.diffuse_color = (color[0], color[1], color[2], color[3])
            logger.info(f"Applied base color: {{color}}")
        
        # Apply roughness
        if "roughness" in material_spec:
            roughness = material_spec["roughness"]
            bsdf.inputs["Roughness"].default_value = roughness
            logger.info(f"Applied roughness: {{roughness}}")
        
        # Apply metallic
        if "metallic" in material_spec:
            metallic = material_spec["metallic"]
            bsdf.inputs["Metallic"].default_value = metallic
            logger.info(f"Applied metallic: {{metallic}}")
        
        # Apply emission
        if "emission" in material_spec:
            emission = material_spec["emission"]
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (emission[0], emission[1], emission[2], 1.0)
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (emission[0], emission[1], emission[2], 1.0)
            logger.info(f"Applied emission: {{emission}}")
        
        # Apply emission strength/intensity
        if "emissiveIntensity" in material_spec:
            intensity = material_spec["emissiveIntensity"]
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = intensity
            logger.info(f"Applied emission intensity: {{intensity}}")

def export_obj(filepath):
    """Export scene to OBJ using manual method for precise control"""
    logger.info(f"Exporting to OBJ: {{filepath}}")
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Get the mesh object
    mesh_obj = None
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh_obj = obj
            break
    
    if not mesh_obj:
        logger.error("No mesh object found for export")
        return
    
    # Log vertex positions before export
    logger.info("Final vertex positions before export:")
    for i, vert in enumerate(mesh_obj.data.vertices[:8]):
        logger.info(f"  Export Vertex {{i}}: {{vert.co[0]:.6f}}, {{vert.co[1]:.6f}}, {{vert.co[2]:.6f}}")
    
    # Manual export to ensure correct vertex coordinates and faces
    try:
        with open(filepath, 'w') as f:
            # Write header
            f.write("# Blender 4.4.3\\n")
            f.write("# www.blender.org\\n")
            mtl_name = os.path.basename(filepath).replace('.obj', '.mtl')
            f.write(f"mtllib {{mtl_name}}\\n")
            f.write(f"o {{mesh_obj.name}}\\n")
            
            # Write vertices using actual mesh coordinates
            for vert in mesh_obj.data.vertices:
                v = vert.co
                f.write(f"v {{v[0]:.6f}} {{v[1]:.6f}} {{v[2]:.6f}}\\n")
            
            # Calculate normals properly for Blender 4.4+
            mesh_obj.data.calc_loop_triangles()
            # Use calc_normals() instead of calc_normals_split() for Blender 4.4+
            if hasattr(mesh_obj.data, 'calc_normals'):
                mesh_obj.data.calc_normals()
            
            # Write normals for each polygon
            written_normals = []
            normal_index_map = {{}}
            
            for poly in mesh_obj.data.polygons:
                normal = poly.normal
                normal_key = (round(normal[0], 4), round(normal[1], 4), round(normal[2], 4))
                
                if normal_key not in normal_index_map:
                    written_normals.append(normal)
                    normal_index_map[normal_key] = len(written_normals)
                    f.write(f"vn {{normal[0]:.4f}} {{normal[1]:.4f}} {{normal[2]:.4f}}\\n")
            
            # Write material usage
            if mesh_obj.data.materials:
                f.write(f"usemtl {{mesh_obj.data.materials[0].name}}\\n")
            
            # Write faces with proper indexing
            logger.info(f"Writing {{len(mesh_obj.data.polygons)}} faces...")
            
            for poly_idx, poly in enumerate(mesh_obj.data.polygons):
                if len(poly.vertices) >= 3:
                    # Write smooth group
                    f.write(f"s {{poly_idx + 1}}\\n")
                    
                    # Get normal index for this polygon
                    normal = poly.normal
                    normal_key = (round(normal[0], 4), round(normal[1], 4), round(normal[2], 4))
                    normal_idx = normal_index_map[normal_key]
                    
                    # Write face with vertex and normal indices (OBJ uses 1-based indexing)
                    face_line = "f"
                    for vert_idx in poly.vertices:
                        face_line += f" {{vert_idx + 1}}//{{normal_idx}}"
                    face_line += "\\n"
                    f.write(face_line)
            
            logger.info(f"Exported {{len(mesh_obj.data.vertices)}} vertices and {{len(mesh_obj.data.polygons)}} faces")
        
        logger.info(f"Manual OBJ export successful: {{filepath}}")
        
        # Create MTL file
        mtl_path = filepath.replace('.obj', '.mtl')
        with open(mtl_path, 'w') as f:
            f.write("# Blender 4.4.3 MTL File\\n")
            f.write("# www.blender.org\\n\\n")
            
            if mesh_obj.data.materials:
                for mat in mesh_obj.data.materials:
                    f.write(f"newmtl {{mat.name}}\\n")
                    f.write("Ns 90.000000\\n")
                    f.write("Ka 0.100000 0.100000 0.100000\\n")
                    f.write("Ni 1.500000\\n")
                    f.write("d 1.000000\\n")
                    f.write("illum 3\\n")
                    
                    # Set diffuse color
                    if hasattr(mat, 'diffuse_color'):
                        color = mat.diffuse_color
                        f.write(f"Kd {{color[0]:.6f}} {{color[1]:.6f}} {{color[2]:.6f}}\\n")
                    else:
                        f.write("Kd 0.800000 0.800000 0.800000\\n")
                    
                    f.write("Ks 0.500000 0.500000 0.500000\\n")
                    f.write("Ke 0.000000 0.000000 0.000000\\n")
                    f.write("\\n")
            else:
                # Create default material
                f.write("newmtl DefaultMaterial\\n")
                f.write("Ns 90.000000\\n")
                f.write("Ka 0.100000 0.100000 0.100000\\n")
                f.write("Kd 0.800000 0.800000 0.800000\\n")
                f.write("Ks 0.500000 0.500000 0.500000\\n")
                f.write("Ke 0.000000 0.000000 0.000000\\n")
                f.write("Ni 1.500000\\n")
                f.write("d 1.000000\\n")
                f.write("illum 3\\n")
        
        logger.info(f"MTL file created: {{mtl_path}}")
            
    except Exception as e:
        logger.error(f"Manual OBJ export failed: {{e}}")
        import traceback
        traceback.print_exc()
        
        # Try fallback using standard Blender export
        logger.info("Attempting fallback export using standard Blender exporter...")
        try:
            # Select and make active
            bpy.ops.object.select_all(action='DESELECT')
            mesh_obj.select_set(True)
            bpy.context.view_layer.objects.active = mesh_obj
            
            # Use Blender's built-in exporter as fallback
            bpy.ops.wm.obj_export(
                filepath=filepath,
                export_selected_objects=True,
                export_materials=True,
                export_uv=True,
                export_normals=True,
                path_mode='COPY'
            )
            logger.info(f"Fallback OBJ export successful: {{filepath}}")
        except Exception as fallback_error:
            logger.error(f"Fallback export also failed: {{fallback_error}}")

def main():
    try:
        args = parse_args()
        logger.info(f"Update script args: {{args}}")
        
        # Load update specification
        with open(args.input, 'r') as f:
            spec = json.load(f)
        
        logger.info(f"Update specification: {{spec}}")
        
        # Import OBJ file
        obj = load_obj(args.obj)
        if not obj:
            logger.error("Failed to load OBJ file")
            sys.exit(1)
        
        # Apply updates
        apply_updates(obj, spec)
        
        # Export updated OBJ
        export_obj(args.output)
        
        logger.info("Update script completed successfully")
        
    except Exception as e:
        logger.error(f"Update script failed: {{e}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
