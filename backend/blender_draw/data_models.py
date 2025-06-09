"""
Data models for Blender drawing commands using Pydantic for validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Tuple, Optional, Literal
from enum import Enum


class Point3D(BaseModel):
    """3D point coordinates."""
    x: float
    y: float
    z: float
    
    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple for Blender API."""
        return (self.x, self.y, self.z)


class Color(BaseModel):
    """RGBA color with validation."""
    r: float = Field(ge=0.0, le=1.0, description="Red component (0-1)")
    g: float = Field(ge=0.0, le=1.0, description="Green component (0-1)")
    b: float = Field(ge=0.0, le=1.0, description="Blue component (0-1)")
    a: float = Field(default=1.0, ge=0.0, le=1.0, description="Alpha component (0-1)")
    
    def to_tuple(self) -> Tuple[float, float, float, float]:
        """Convert to RGBA tuple for Blender API."""
        return (self.r, self.g, self.b, self.a)
    
    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        """Create color from hex string (#RRGGBB or #RRGGBBAA)."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            hex_color += 'FF'
        elif len(hex_color) != 8:
            raise ValueError("Invalid hex color format")
        
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        a = int(hex_color[6:8], 16) / 255.0
        
        return cls(r=r, g=g, b=b, a=a)


class PrimitiveType(str, Enum):
    """Supported primitive types."""
    CUBE = "cube"
    SPHERE = "sphere"
    CYLINDER = "cylinder"
    CONE = "cone"
    PLANE = "plane"
    TORUS = "torus"


class LineCommand(BaseModel):
    """Command to draw a line or polyline."""
    points: List[Point3D] = Field(min_items=2, description="Line vertices")
    color: Color = Field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0))
    thickness: float = Field(default=0.01, gt=0.0, description="Line thickness")
    name: str = Field(default="Line", description="Object name")


class CurveCommand(BaseModel):
    """Command to draw a smooth curve."""
    control_points: List[Point3D] = Field(min_items=2, description="Curve control points")
    color: Color = Field(default_factory=lambda: Color(r=1.0, g=0.5, b=0.0))
    thickness: float = Field(default=0.02, gt=0.0, description="Curve thickness")
    resolution: int = Field(default=12, ge=3, le=64, description="Curve resolution")
    name: str = Field(default="Curve", description="Object name")


class MeshCommand(BaseModel):
    """Command to create a custom mesh."""
    vertices: List[Point3D] = Field(min_items=3, description="Mesh vertices")
    faces: List[List[int]] = Field(description="Face indices (triangles/quads)")
    color: Color = Field(default_factory=lambda: Color(r=0.8, g=0.8, b=0.8))
    name: str = Field(default="Mesh", description="Object name")
    smooth: bool = Field(default=True, description="Apply smooth shading")
    
    @validator('faces')
    def validate_faces(cls, v, values):
        """Validate face indices are valid."""
        if 'vertices' in values:
            vertex_count = len(values['vertices'])
            for face in v:
                if len(face) < 3:
                    raise ValueError("Faces must have at least 3 vertices")
                for idx in face:
                    if idx < 0 or idx >= vertex_count:
                        raise ValueError(f"Face index {idx} out of range")
        return v


class PrimitiveCommand(BaseModel):
    """Command to create a primitive shape."""
    primitive_type: PrimitiveType
    location: Point3D = Field(default_factory=lambda: Point3D(x=0, y=0, z=0))
    scale: Point3D = Field(default_factory=lambda: Point3D(x=1, y=1, z=1))
    rotation: Point3D = Field(default_factory=lambda: Point3D(x=0, y=0, z=0))
    color: Color = Field(default_factory=lambda: Color(r=0.6, g=0.6, b=1.0))
    name: str = Field(default="Primitive", description="Object name")
    
    # Primitive-specific parameters
    subdivisions: int = Field(default=2, ge=1, le=6, description="Subdivision level")
    radius: float = Field(default=1.0, gt=0.0, description="Radius for spheres/cylinders/cones")
    height: float = Field(default=2.0, gt=0.0, description="Height for cylinders/cones")


class DrawingSession(BaseModel):
    """Complete drawing session with multiple commands."""
    session_id: str = Field(description="Unique session identifier")
    clear_scene: bool = Field(default=True, description="Clear scene before drawing")
    commands: List[
        Tuple[
            Literal["line", "curve", "mesh", "primitive"],
            dict
        ]
    ] = Field(description="List of drawing commands")
    output_format: Literal["blend", "obj"] = Field(default="obj", description="Export format")
    output_name: str = Field(default="drawing", description="Output file name")
    
    @validator('commands')
    def validate_commands(cls, v):
        """Validate command structure."""
        valid_types = {"line", "curve", "mesh", "primitive"}
        for cmd_type, cmd_data in v:
            if cmd_type not in valid_types:
                raise ValueError(f"Invalid command type: {cmd_type}")
        return v
