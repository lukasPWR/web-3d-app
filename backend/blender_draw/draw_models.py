"""
Core Blender drawing functions for programmatic 3D model creation.
Uses Blender's data API for reliable headless operation.
"""

import bpy
import bmesh
import mathutils
import os
import uuid
from typing import List, Tuple, Optional, Union
from pathlib import Path

# Use simple models when running in Blender (no pydantic dependency)
try:
    from .data_models import Point3D, Color, LineCommand, CurveCommand, MeshCommand, PrimitiveCommand
    USE_PYDANTIC = True
except ImportError:
    from .simple_models import Point3D, Color, parse_command_data
    USE_PYDANTIC = False


def clear_scene() -> None:
    """
    Clear all mesh objects from the current Blender scene.
    Keeps cameras and lights intact.
    """
    # Select all mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    
    # Delete all mesh objects using data API
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Clean up orphaned mesh data
    for mesh in bpy.data.meshes:
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    
    # Clean up orphaned materials
    for material in bpy.data.materials:
        if material.users == 0:
            bpy.data.materials.remove(material)


def _create_material(name: str, color: Color):
    """
    Create a material with specified color using Principled BSDF.
    
    Args:
        name: Material name
        color: RGBA color
        
    Returns:
        Created material object
    """
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    
    # Get the Principled BSDF node
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    
    if principled:
        # Set base color
        principled.inputs["Base Color"].default_value = color.to_tuple()
        # Set some default material properties
        principled.inputs["Roughness"].default_value = 0.5
        principled.inputs["Metallic"].default_value = 0.0
    
    return material


def draw_line(points: List[Point3D], color: Color, thickness: float = 0.01, name: str = "Line") -> str:
    """
    Draw a line or polyline in Blender using mesh geometry.
    
    Args:
        points: List of 3D points defining the line
        color: Line color
        thickness: Line thickness (converted to mesh)
        name: Object name
        
    Returns:
        Name of created object
        
    Raises:
        ValueError: If less than 2 points provided
    """
    if len(points) < 2:
        raise ValueError("Line requires at least 2 points")
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Link to scene
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh for easier mesh manipulation
    bm = bmesh.new()
    
    # Add vertices
    vertices = []
    for point in points:
        vert = bm.verts.new(point.to_tuple())
        vertices.append(vert)
    
    # Create edges between consecutive vertices
    for i in range(len(vertices) - 1):
        bm.edges.new([vertices[i], vertices[i + 1]])
    
    # Convert to mesh with thickness using solidify
    if thickness > 0:
        # Create geometry for line thickness
        bmesh.ops.solidify(bm, geom=bm.faces[:] + bm.edges[:], thickness=thickness)
    
    # Update mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Create and assign material
    material = _create_material(f"{name}_material", color)
    obj.data.materials.append(material)
    
    return obj.name


def draw_curve(control_points: List[Point3D], color: Color, thickness: float = 0.02, 
               resolution: int = 12, name: str = "Curve") -> str:
    """
    Draw a smooth curve using Blender's curve object.
    
    Args:
        control_points: Curve control points
        color: Curve color
        thickness: Curve thickness
        resolution: Curve resolution
        name: Object name
        
    Returns:
        Name of created object
    """
    # Create curve data
    curve_data = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = resolution
    curve_data.bevel_depth = thickness / 2
    curve_data.bevel_resolution = 4
    
    # Create spline
    spline = curve_data.splines.new('NURBS')
    spline.points.add(len(control_points) - 1)
    
    # Set control points
    for i, point in enumerate(control_points):
        spline.points[i].co = (point.x, point.y, point.z, 1.0)
    
    # Create object
    curve_obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # Create and assign material
    material = _create_material(f"{name}_material", color)
    curve_obj.data.materials.append(material)
    
    return curve_obj.name


def draw_mesh(vertices: List[Point3D], faces: List[List[int]], color: Color, 
              smooth: bool = True, name: str = "Mesh") -> str:
    """
    Create a custom mesh from vertices and faces.
    
    Args:
        vertices: Mesh vertices
        faces: Face definitions (list of vertex indices)
        color: Mesh color
        smooth: Apply smooth shading
        name: Object name
        
    Returns:
        Name of created object
    """
    # Create mesh
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Convert points to tuples
    verts = [point.to_tuple() for point in vertices]
    
    # Create mesh from vertices and faces
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Apply smooth shading if requested
    if smooth:
        for face in mesh.polygons:
            face.use_smooth = True
    
    # Link to scene
    bpy.context.collection.objects.link(obj)
    
    # Create and assign material
    material = _create_material(f"{name}_material", color)
    obj.data.materials.append(material)
    
    # Recalculate normals
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return obj.name


def draw_primitive(primitive_type: str, location: Point3D, scale: Point3D, 
                  rotation: Point3D, color: Color, name: str = "Primitive",
                  **kwargs) -> str:
    """
    Create a primitive shape (cube, sphere, cylinder, etc.).
    
    Args:
        primitive_type: Type of primitive ('cube', 'sphere', 'cylinder', 'cone', 'plane', 'torus')
        location: Object location
        scale: Object scale
        rotation: Object rotation (in degrees)
        color: Object color
        name: Object name
        **kwargs: Additional primitive-specific parameters
        
    Returns:
        Name of created object
    """
    # Map primitive types to Blender operators
    primitive_ops = {
        'cube': 'mesh.primitive_cube_add',
        'sphere': 'mesh.primitive_uv_sphere_add', 
        'cylinder': 'mesh.primitive_cylinder_add',
        'cone': 'mesh.primitive_cone_add',
        'plane': 'mesh.primitive_plane_add',
        'torus': 'mesh.primitive_torus_add'
    }
    
    if primitive_type not in primitive_ops:
        raise ValueError(f"Unsupported primitive type: {primitive_type}")
    
    # Set location for primitive creation
    bpy.context.scene.cursor.location = location.to_tuple()
    
    # Create primitive with specific parameters
    op_name = primitive_ops[primitive_type]
    params = {'location': location.to_tuple()}
    
    if primitive_type in ['sphere', 'cylinder', 'cone']:
        params['radius'] = kwargs.get('radius', 1.0)
    
    if primitive_type in ['cylinder', 'cone']:
        params['depth'] = kwargs.get('height', 2.0)
    
    if primitive_type == 'sphere':
        params['subdivisions'] = kwargs.get('subdivisions', 2)
    
    # Execute the operator
    op_name = primitive_ops[primitive_type]
    if op_name == 'mesh.primitive_cube_add':
        bpy.ops.mesh.primitive_cube_add(**params)
    elif op_name == 'mesh.primitive_uv_sphere_add':
        bpy.ops.mesh.primitive_uv_sphere_add(**params)
    elif op_name == 'mesh.primitive_cylinder_add':
        bpy.ops.mesh.primitive_cylinder_add(**params)
    elif op_name == 'mesh.primitive_cone_add':
        bpy.ops.mesh.primitive_cone_add(**params)
    elif op_name == 'mesh.primitive_plane_add':
        bpy.ops.mesh.primitive_plane_add(**params)
    elif op_name == 'mesh.primitive_torus_add':
        bpy.ops.mesh.primitive_torus_add(**params)
    
    # Get the created object (it's the active object)
    obj = bpy.context.active_object
    obj.name = name
    
    # Apply transformations
    obj.location = location.to_tuple()
    obj.scale = scale.to_tuple()
    
    # Convert rotation from degrees to radians
    obj.rotation_euler = (
        mathutils.Vector(rotation.to_tuple()) * (3.14159 / 180.0)
    )
    
    # Create and assign material
    material = _create_material(f"{name}_material", color)
    obj.data.materials.append(material)
    
    return obj.name


def save_blend_file(filepath: str) -> str:
    """
    Save the current Blender scene to a .blend file.
    
    Args:
        filepath: Output file path
        
    Returns:
        Absolute path to saved file
    """
    abs_path = os.path.abspath(filepath)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Save the file
    bpy.ops.wm.save_as_mainfile(filepath=abs_path)
    
    return abs_path


def export_obj_file(filepath: str, selected_only: bool = False) -> str:
    """
    Export the scene (or selected objects) to an OBJ file.
    Compatible with Blender 4.4+ and older versions.
    
    Args:
        filepath: Output file path
        selected_only: Export only selected objects
        
    Returns:
        Absolute path to exported file
    """
    abs_path = os.path.abspath(filepath)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    # Try new Blender 4.4+ export API first
    try:
        # New API in Blender 4.4+
        bpy.ops.wm.obj_export(
            filepath=abs_path,
            export_selected_objects=selected_only,
            export_materials=True,
            export_uv=True,
            export_normals=True
        )
        return abs_path
    except AttributeError:
        # Fallback to old API for Blender < 4.4
        try:
            bpy.ops.export_scene.obj(
                filepath=abs_path,
                use_selection=selected_only,
                use_materials=True,
                use_uvs=True,
                use_normals=True
            )
            return abs_path
        except AttributeError:
            # If both fail, try manual export or alternative method
            print(f"Warning: OBJ export not available, saving as .blend instead")
            blend_path = abs_path.replace('.obj', '.blend')
            return save_blend_file(blend_path)


def execute_drawing_session(session_data: dict) -> Tuple[str, str]:
    """
    Execute a complete drawing session with multiple commands.
    
    Args:
        session_data: Drawing session data
        
    Returns:
        Tuple of (session_id, output_file_path)
    """
    session_id = session_data.get("session_id", str(uuid.uuid4()))
    clear_scene_flag = session_data.get("clear_scene", True)
    commands = session_data.get("commands", [])
    output_format = session_data.get("output_format", "obj")
    output_name = session_data.get("output_name", "drawing")
    
    # Clear scene if requested
    if clear_scene_flag:
        clear_scene()
    
    created_objects = []
    
    # Execute each command
    for cmd_type, cmd_data in commands:
        try:
            if USE_PYDANTIC:
                # Use pydantic models for validation
                if cmd_type == "line":
                    command = LineCommand(**cmd_data)
                    obj_name = draw_line(
                        command.points, command.color, command.thickness, command.name
                    )
                elif cmd_type == "curve":
                    command = CurveCommand(**cmd_data)
                    obj_name = draw_curve(
                        command.control_points, command.color, 
                        command.thickness, command.resolution, command.name
                    )
                elif cmd_type == "mesh":
                    command = MeshCommand(**cmd_data)
                    obj_name = draw_mesh(
                        command.vertices, command.faces, 
                        command.color, command.smooth, command.name
                    )
                elif cmd_type == "primitive":
                    command = PrimitiveCommand(**cmd_data)
                    obj_name = draw_primitive(
                        command.primitive_type.value, command.location,
                        command.scale, command.rotation, command.color, 
                        command.name, **cmd_data
                    )
            else:
                # Use simple parsing without pydantic
                parsed_data = parse_command_data(cmd_type, cmd_data)
                
                if cmd_type == "line":
                    obj_name = draw_line(
                        parsed_data["points"], parsed_data["color"], 
                        parsed_data["thickness"], parsed_data["name"]
                    )
                elif cmd_type == "curve":
                    obj_name = draw_curve(
                        parsed_data["control_points"], parsed_data["color"],
                        parsed_data["thickness"], parsed_data["resolution"], 
                        parsed_data["name"]
                    )
                elif cmd_type == "mesh":
                    obj_name = draw_mesh(
                        parsed_data["vertices"], parsed_data["faces"],
                        parsed_data["color"], parsed_data["smooth"], 
                        parsed_data["name"]
                    )
                elif cmd_type == "primitive":
                    obj_name = draw_primitive(
                        parsed_data["primitive_type"], parsed_data["location"],
                        parsed_data["scale"], parsed_data["rotation"], 
                        parsed_data["color"], parsed_data["name"],
                        subdivisions=parsed_data["subdivisions"],
                        radius=parsed_data["radius"],
                        height=parsed_data["height"]
                    )
            
            created_objects.append(obj_name)
                
        except Exception as e:
            print(f"Error executing {cmd_type} command: {e}")
            continue
    
    # Generate output file path
    output_dir = Path("./output/drawings")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_format == "blend":
        output_path = output_dir / f"{output_name}_{session_id}.blend"
        final_path = save_blend_file(str(output_path))
    else:
        output_path = output_dir / f"{output_name}_{session_id}.obj"
        final_path = export_obj_file(str(output_path))
    
    return session_id, final_path
