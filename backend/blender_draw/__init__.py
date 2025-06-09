"""
Blender drawing module for programmatic 3D model creation.
"""

from .draw_models import (
    draw_line,
    draw_curve,
    draw_mesh,
    draw_primitive,
    clear_scene,
    save_blend_file,
    export_obj_file,
    execute_drawing_session,
)

# Try to import pydantic models, fall back to simple models if not available
try:
    from .data_models import (
        Point3D,
        Color,
        LineCommand,
        CurveCommand,
        MeshCommand,
        PrimitiveCommand,
        DrawingSession,
    )
    PYDANTIC_AVAILABLE = True
except ImportError:
    # When running in Blender, use simple models instead
    from .simple_models import Point3D, Color
    PYDANTIC_AVAILABLE = False
    
    # Create dummy classes for API compatibility
    class LineCommand:
        pass
    class CurveCommand:
        pass
    class MeshCommand:
        pass
    class PrimitiveCommand:
        pass
    class DrawingSession:
        pass

__all__ = [
    "draw_line",
    "draw_curve", 
    "draw_mesh",
    "draw_primitive",
    "clear_scene",
    "save_blend_file",
    "export_obj_file",
    "execute_drawing_session",
    "Point3D",
    "Color",
    "LineCommand",
    "CurveCommand",
    "MeshCommand",
    "PrimitiveCommand",
    "DrawingSession",
    "PYDANTIC_AVAILABLE",
]
