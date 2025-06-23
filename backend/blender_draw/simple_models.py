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


def parse_command_data(cmd_type: str, cmd_data: dict) -> dict:
    """
    Parse command data from dictionary format to our internal format.
    
    Args:
        cmd_type: Command type
        cmd_data: Command data dictionary
        
    Returns:
        Parsed command data
    """
    if cmd_type == "line":
        # Parse line command
        points = []
        for point_data in cmd_data.get("points", []):
            if isinstance(point_data, dict):
                points.append(Point3D(
                    x=point_data.get("x", 0),
                    y=point_data.get("y", 0),
                    z=point_data.get("z", 0)
                ))
            elif isinstance(point_data, (list, tuple)) and len(point_data) >= 3:
                points.append(Point3D(x=point_data[0], y=point_data[1], z=point_data[2]))
        
        color_data = cmd_data.get("color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})
        if isinstance(color_data, dict):
            color = Color(
                r=color_data.get("r", 1.0),
                g=color_data.get("g", 1.0),
                b=color_data.get("b", 1.0),
                a=color_data.get("a", 1.0)
            )
        else:
            # Handle hex color
            color = Color.from_hex(str(color_data))
        
        return {
            "points": points,
            "color": color,
            "thickness": cmd_data.get("thickness", 0.01),
            "name": cmd_data.get("name", "Line")
        }
    
    elif cmd_type == "curve":
        # Parse curve command
        points = []
        for point_data in cmd_data.get("control_points", []):
            if isinstance(point_data, dict):
                points.append(Point3D(
                    x=point_data.get("x", 0),
                    y=point_data.get("y", 0),
                    z=point_data.get("z", 0)
                ))
            elif isinstance(point_data, (list, tuple)) and len(point_data) >= 3:
                points.append(Point3D(x=point_data[0], y=point_data[1], z=point_data[2]))
        
        color_data = cmd_data.get("color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})
        if isinstance(color_data, dict):
            color = Color(
                r=color_data.get("r", 1.0),
                g=color_data.get("g", 1.0),
                b=color_data.get("b", 1.0),
                a=color_data.get("a", 1.0)
            )
        else:
            color = Color.from_hex(str(color_data))
        
        return {
            "control_points": points,
            "color": color,
            "thickness": cmd_data.get("thickness", 0.02),
            "resolution": cmd_data.get("resolution", 12),
            "name": cmd_data.get("name", "Curve")
        }
    
    elif cmd_type == "mesh":
        # Parse mesh command
        vertices = []
        for vertex_data in cmd_data.get("vertices", []):
            if isinstance(vertex_data, dict):
                vertices.append(Point3D(
                    x=vertex_data.get("x", 0),
                    y=vertex_data.get("y", 0),
                    z=vertex_data.get("z", 0)
                ))
            elif isinstance(vertex_data, (list, tuple)) and len(vertex_data) >= 3:
                vertices.append(Point3D(x=vertex_data[0], y=vertex_data[1], z=vertex_data[2]))
        
        color_data = cmd_data.get("color", {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0})
        if isinstance(color_data, dict):
            color = Color(
                r=color_data.get("r", 1.0),
                g=color_data.get("g", 1.0),
                b=color_data.get("b", 1.0),
                a=color_data.get("a", 1.0)
            )
        else:
            color = Color.from_hex(str(color_data))
        
        return {
            "vertices": vertices,
            "faces": cmd_data.get("faces", []),
            "color": color,
            "smooth": cmd_data.get("smooth", True),
            "name": cmd_data.get("name", "Mesh")
        }
    
    elif cmd_type == "primitive":
        # Parse primitive command - fix the main issue here
        primitive_type = cmd_data.get("primitive_type", "cube")
        
        # Parse location
        location_data = cmd_data.get("location", {"x": 0, "y": 0, "z": 0})
        if isinstance(location_data, dict):
            location = Point3D(
                x=location_data.get("x", 0),
                y=location_data.get("y", 0),
                z=location_data.get("z", 0)
            )
        elif isinstance(location_data, (list, tuple)) and len(location_data) >= 3:
            location = Point3D(x=location_data[0], y=location_data[1], z=location_data[2])
        else:
            location = Point3D(x=0, y=0, z=0)
        
        # Parse scale
        scale_data = cmd_data.get("scale", {"x": 1, "y": 1, "z": 1})
        if isinstance(scale_data, dict):
            scale = Point3D(
                x=scale_data.get("x", 1),
                y=scale_data.get("y", 1),
                z=scale_data.get("z", 1)
            )
        elif isinstance(scale_data, (list, tuple)) and len(scale_data) >= 3:
            scale = Point3D(x=scale_data[0], y=scale_data[1], z=scale_data[2])
        else:
            scale = Point3D(x=1, y=1, z=1)
        
        # Parse rotation
        rotation_data = cmd_data.get("rotation", {"x": 0, "y": 0, "z": 0})
        if isinstance(rotation_data, dict):
            rotation = Point3D(
                x=rotation_data.get("x", 0),
                y=rotation_data.get("y", 0),
                z=rotation_data.get("z", 0)
            )
        elif isinstance(rotation_data, (list, tuple)) and len(rotation_data) >= 3:
            rotation = Point3D(x=rotation_data[0], y=rotation_data[1], z=rotation_data[2])
        else:
            rotation = Point3D(x=0, y=0, z=0)
        
        # Parse color
        color_data = cmd_data.get("color", {"r": 0.5, "g": 0.5, "b": 1.0, "a": 1.0})
        if isinstance(color_data, dict):
            color = Color(
                r=color_data.get("r", 0.5),
                g=color_data.get("g", 0.5),
                b=color_data.get("b", 1.0),
                a=color_data.get("a", 1.0)
            )
        else:
            # Handle hex color string
            color = Color.from_hex(str(color_data))
        
        return {
            "primitive_type": primitive_type,
            "location": location,
            "scale": scale,
            "rotation": rotation,
            "color": color,
            "name": cmd_data.get("name", "Primitive"),
            "subdivisions": cmd_data.get("subdivisions", 2),
            "radius": cmd_data.get("radius", 1.0),
            "height": cmd_data.get("height", 2.0)
        }
    
    elif cmd_type == "custom_coords":
        # Parse custom coordinates command
        coordinates_text = cmd_data.get("coordinates_text", "")
        color_data = cmd_data.get("color", {"r": 0.8, "g": 0.8, "b": 0.8, "a": 1.0})
        
        if isinstance(color_data, dict):
            color = Color(
                r=color_data.get("r", 0.8),
                g=color_data.get("g", 0.8),
                b=color_data.get("b", 0.8),
                a=color_data.get("a", 1.0)
            )
        else:
            # Handle hex color string
            color = Color.from_hex(str(color_data))
        
        return {
            "coordinates_text": coordinates_text,
            "color": color,
            "name": cmd_data.get("name", "CustomMesh"),
            "use_convex_hull": cmd_data.get("use_convex_hull", True)
        }
    
    else:
        raise ValueError(f"Unknown command type: {cmd_type}")
