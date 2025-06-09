"""
Simple data models for Blender drawing that don't require pydantic.
Used when running inside Blender's Python environment.
"""

from typing import List, Tuple, Optional, Dict, Any


class Point3D:
    """Simple 3D point coordinates."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = x
        self.y = y
        self.z = z
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Point3D":
        """Create from dictionary."""
        return cls(data.get('x', 0.0), data.get('y', 0.0), data.get('z', 0.0))
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple for Blender API."""
        return (self.x, self.y, self.z)


class Color:
    """Simple RGBA color."""
    
    def __init__(self, r: float = 1.0, g: float = 1.0, b: float = 1.0, a: float = 1.0):
        self.r = max(0.0, min(1.0, r))
        self.g = max(0.0, min(1.0, g))
        self.b = max(0.0, min(1.0, b))
        self.a = max(0.0, min(1.0, a))
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Color":
        """Create from dictionary."""
        return cls(
            data.get('r', 1.0),
            data.get('g', 1.0),
            data.get('b', 1.0),
            data.get('a', 1.0)
        )
    
    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        """Create color from hex string."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'FF'
        elif len(hex_color) != 8:
            raise ValueError("Invalid hex color format")
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0
        
        return cls(r, g, b, a)
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convert to RGBA tuple for Blender API."""
        return (self.r, self.g, self.b, self.a)


def parse_command_data(cmd_type: str, cmd_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse command data into appropriate format."""
    
    if cmd_type == "line":
        return {
            "points": [Point3D.from_dict(p) for p in cmd_data.get("points", [])],
            "color": Color.from_dict(cmd_data.get("color", {})),
            "thickness": cmd_data.get("thickness", 0.01),
            "name": cmd_data.get("name", "Line")
        }
    
    elif cmd_type == "curve":
        return {
            "control_points": [Point3D.from_dict(p) for p in cmd_data.get("control_points", [])],
            "color": Color.from_dict(cmd_data.get("color", {})),
            "thickness": cmd_data.get("thickness", 0.02),
            "resolution": cmd_data.get("resolution", 12),
            "name": cmd_data.get("name", "Curve")
        }
    
    elif cmd_type == "mesh":
        return {
            "vertices": [Point3D.from_dict(v) for v in cmd_data.get("vertices", [])],
            "faces": cmd_data.get("faces", []),
            "color": Color.from_dict(cmd_data.get("color", {})),
            "smooth": cmd_data.get("smooth", True),
            "name": cmd_data.get("name", "Mesh")
        }
    
    elif cmd_type == "primitive":
        return {
            "primitive_type": cmd_data.get("primitive_type", "cube"),
            "location": Point3D.from_dict(cmd_data.get("location", {})),
            "scale": Point3D.from_dict(cmd_data.get("scale", {"x": 1, "y": 1, "z": 1})),
            "rotation": Point3D.from_dict(cmd_data.get("rotation", {})),
            "color": Color.from_dict(cmd_data.get("color", {})),
            "name": cmd_data.get("name", "Primitive"),
            "subdivisions": cmd_data.get("subdivisions", 2),
            "radius": cmd_data.get("radius", 1.0),
            "height": cmd_data.get("height", 2.0)
        }
    
    return cmd_data
