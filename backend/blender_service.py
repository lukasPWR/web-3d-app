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
    
    logger.info("Reading session data from: {session_file}")
    with open(r"{session_file}", "r") as f:
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

logger.info(f"Writing result to: {result_file}")
with open(r"{result_file}", "w") as f:
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
