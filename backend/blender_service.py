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
        """
        Initialize the Blender service.
        
        Args:
            blender_executable: Path to Blender executable
        """
        self.blender_executable = blender_executable
        self.script_template = self._get_execution_script_template()
    
    def _get_execution_script_template(self) -> str:
        """Get the Python script template for Blender execution."""
        return '''
import sys
import json
import os
from pathlib import Path

# Get the directory where this script is being executed from
script_dir = Path(__file__).parent
backend_dir = script_dir.parent if script_dir.name.startswith('tmp') else script_dir

# Find the actual backend directory by looking for blender_draw folder
current_dir = Path(os.getcwd())
backend_candidates = [
    current_dir,
    current_dir / "backend",
    Path(__file__).parent.parent,
    Path(__file__).parent.parent / "backend"
]

backend_dir = None
for candidate in backend_candidates:
    if (candidate / "blender_draw").exists():
        backend_dir = candidate
        break

if not backend_dir:
    raise ImportError(f"Could not find blender_draw module. Searched in: {{[str(c) for c in backend_candidates]}}")

# Add the backend directory to Python path
sys.path.insert(0, str(backend_dir))

# Now import our drawing module
try:
    from blender_draw.draw_models import execute_drawing_session
    
    # Read session data from JSON file - use raw string or forward slashes
    session_file = r"{session_file}"
    result_file = r"{result_file}"
    
    with open(session_file, "r") as f:
        session_data = json.load(f)
    
    # Execute drawing session
    session_id, output_path = execute_drawing_session(session_data)
    
    # Write result to output file
    result = {{
        "success": True,
        "session_id": session_id,
        "output_path": str(output_path),
        "error": None
    }}
    
    with open(result_file, "w") as f:
        json.dump(result, f)
        
except Exception as e:
    import traceback
    error_details = {{
        "error": str(e),
        "traceback": traceback.format_exc(),
        "sys_path": sys.path,
        "working_dir": os.getcwd(),
        "backend_dir": str(backend_dir) if backend_dir else "None"
    }}
    
    # Write error to output file
    result = {{
        "success": False,
        "session_id": None,
        "output_path": None,
        "error": str(e),
        "details": error_details
    }}
    
    with open(r"{result_file}", "w") as f:
        json.dump(result, f)
'''
    
    def execute_drawing_session(self, session_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Execute a drawing session in headless Blender.
        
        Args:
            session_data: Drawing session configuration
            
        Returns:
            Tuple of (success, output_file_path, error_message)
        """
        # Generate unique session ID if not provided
        if "session_id" not in session_data:
            session_data["session_id"] = str(uuid.uuid4())
        
        # Create temporary files for communication
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write session data to JSON file
            session_file = temp_path / "session.json"
            with open(session_file, "w") as f:
                json.dump(session_data, f, default=str)
            
            # Create result file path
            result_file = temp_path / "result.json"
            
            # Create execution script with properly escaped paths
            script_content = self.script_template.format(
                session_file=str(session_file).replace('\\', '\\\\'),
                result_file=str(result_file).replace('\\', '\\\\')
            )
            
            script_file = temp_path / "execute_drawing.py"
            with open(script_file, "w", encoding='utf-8') as f:
                f.write(script_content)
            
            try:
                # Execute Blender in headless mode
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
                    timeout=300,  # 5 minute timeout
                    cwd=str(Path(__file__).parent)  # Set working directory to backend folder
                )
                
                print(f"Blender stdout: {result.stdout}")
                print(f"Blender stderr: {result.stderr}")
                
                # Read result
                if result_file.exists():
                    with open(result_file, "r") as f:
                        execution_result = json.load(f)
                    
                    if execution_result["success"]:
                        return True, execution_result["output_path"], None
                    else:
                        error_msg = execution_result.get("error", "Unknown error")
                        if "details" in execution_result:
                            error_msg += f"\nDetails: {execution_result['details']}"
                        return False, None, error_msg
                else:
                    return False, None, f"Blender execution failed. stdout: {result.stdout}, stderr: {result.stderr}"
                    
            except subprocess.TimeoutExpired:
                return False, None, "Blender execution timed out"
            except Exception as e:
                return False, None, f"Execution error: {str(e)}"
    
    def create_line(self, points: list, color: str = "#ffffff", 
                   thickness: float = 0.01, name: str = "Line") -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a simple line drawing.
        
        Args:
            points: List of [x, y, z] coordinates
            color: Hex color string
            thickness: Line thickness
            name: Object name
            
        Returns:
            Tuple of (success, output_file_path, error_message)
        """
        # Convert inputs to proper format without importing blender modules
        point_objects = [{"x": p[0], "y": p[1], "z": p[2]} for p in points]
        
        # Convert hex color to RGBA dict
        hex_color = color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'FF'
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0
        
        color_obj = {"r": r, "g": g, "b": b, "a": a}
        
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
        """
        Create a primitive shape.
        
        Args:
            primitive_type: Type of primitive ('cube', 'sphere', etc.)
            location: [x, y, z] location
            scale: [x, y, z] scale
            color: Hex color string
            name: Object name
            
        Returns:
            Tuple of (success, output_file_path, error_message)
        """
        # Convert hex color to RGBA dict
        hex_color = color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'FF'
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0
        
        color_obj = {"r": r, "g": g, "b": b, "a": a}
        
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
