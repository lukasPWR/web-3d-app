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

# Find backend directory containing blender_draw module
backend_candidates = [
    Path(os.getcwd()),
    Path(os.getcwd()) / "backend",
    Path(__file__).parent.parent,
    Path(__file__).parent.parent / "backend"
]

backend_dir = None
for candidate in backend_candidates:
    if (candidate / "blender_draw").exists():
        backend_dir = candidate
        break

if not backend_dir:
    raise ImportError(f"Could not find blender_draw module")

sys.path.insert(0, str(backend_dir))

try:
    from blender_draw.draw_models import execute_drawing_session
    
    with open(r"{session_file}", "r") as f:
        session_data = json.load(f)
    
    session_id, output_path = execute_drawing_session(session_data)
    
    result = {{
        "success": True,
        "session_id": session_id,
        "output_path": str(output_path),
        "error": None
    }}
    
except Exception as e:
    import traceback
    result = {{
        "success": False,
        "session_id": None,
        "output_path": None,
        "error": str(e),
        "traceback": traceback.format_exc()
    }}

with open(r"{result_file}", "w") as f:
    json.dump(result, f)
'''
    
    def execute_drawing_session(self, session_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
        """Execute a drawing session in headless Blender."""
        if "session_id" not in session_data:
            session_data["session_id"] = str(uuid.uuid4())
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create session and result files
            session_file = temp_path / "session.json"
            result_file = temp_path / "result.json"
            script_file = temp_path / "execute_drawing.py"
            
            # Write files
            with open(session_file, "w") as f:
                json.dump(session_data, f, default=str)
            
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
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                cwd=str(Path(__file__).parent)
            )
            
            if result_file.exists():
                with open(result_file, "r") as f:
                    execution_result = json.load(f)
                
                if execution_result["success"]:
                    return True, execution_result["output_path"], None
                else:
                    return False, None, execution_result.get("error", "Unknown error")
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
