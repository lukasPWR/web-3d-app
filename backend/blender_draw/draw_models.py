"""
Core Blender drawing functions for programmatic 3D model creation.
Uses Blender's data API for reliable headless operation.
"""

import bpy  # type: ignore
import bmesh  # type: ignore
import mathutils  # type: ignore
import os
import uuid
from typing import List, Tuple
from pathlib import Path

# Use simple models - no pydantic dependency
from .simple_models import Point3D, Color, parse_command_data


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


def optimize_vertices_advanced(vertices: List[Tuple[float, float, float]], precision: int = 3, 
                             use_float32: bool = True) -> Tuple[List[Tuple[float, float, float]], List[int]]:
    """
    Advanced vertex optimization with Float32Array-like precision and deduplication.
    
    Args:
        vertices: List of vertex coordinates
        precision: Decimal precision for quantization
        use_float32: Use Float32 precision instead of Float64
        
    Returns:
        Tuple of (unique_vertices, index_mapping)
    """
    import struct
    
    factor = 10 ** precision
    vertex_map = {}
    unique_vertices = []
    indices = []
    
    for vertex in vertices:
        x, y, z = vertex
        
        # Apply Float32 precision if requested
        if use_float32:
            # Convert to Float32 precision (4 bytes) like JavaScript Float32Array
            x = struct.unpack('f', struct.pack('f', x))[0]
            y = struct.unpack('f', struct.pack('f', y))[0] 
            z = struct.unpack('f', struct.pack('f', z))[0]
        
        # Quantize coordinates
        x = round(x * factor) / factor
        y = round(y * factor) / factor
        z = round(z * factor) / factor
        
        key = (x, y, z)
        if key not in vertex_map:
            vertex_map[key] = len(unique_vertices)
            unique_vertices.append(key)
        
        indices.append(vertex_map[key])
    
    return unique_vertices, indices


def compress_geometry_data(vertices: List[Tuple[float, float, float]], 
                          faces: List[List[int]] = None) -> dict:
    """
    Compress geometry data for optimal storage and transmission.
    
    Args:
        vertices: Vertex coordinates
        faces: Face definitions
        
    Returns:
        Dictionary with compressed geometry data
    """
    # Optimize vertices with deduplication
    unique_vertices, vertex_indices = optimize_vertices_advanced(vertices, precision=3, use_float32=True)
    
    # Calculate compression ratio
    original_count = len(vertices)
    compressed_count = len(unique_vertices)
    compression_ratio = compressed_count / original_count if original_count > 0 else 1.0
    
    # Flatten vertex data for efficient storage
    flattened_vertices = []
    for vertex in unique_vertices:
        flattened_vertices.extend(vertex)
    
    result = {
        "vertices": flattened_vertices,  # Flat array like Float32Array
        "vertex_count": len(unique_vertices),
        "original_vertex_count": original_count,
        "compression_ratio": compression_ratio,
        "vertex_indices": vertex_indices
    }
    
    if faces:
        # Remap face indices to use compressed vertices
        compressed_faces = []
        for face in faces:
            compressed_face = [vertex_indices[i] for i in face if i < len(vertex_indices)]
            if len(compressed_face) >= 3:  # Valid face
                compressed_faces.append(compressed_face)
        result["faces"] = compressed_faces
    
    return result


def draw_line(points: List[Point3D], color: Color, thickness: float = 0.01, name: str = "Line") -> str:
    """
    Draw a line or polyline in Blender using mesh geometry with vertex optimization.
    
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
    
    # Convert points to tuples and optimize
    vertices = [point.to_tuple() for point in points]
    compressed_data = compress_geometry_data(vertices)
    
    print(f"Line vertices optimized: {compressed_data['original_vertex_count']} -> {compressed_data['vertex_count']} "
          f"(ratio: {compressed_data['compression_ratio']:.3f})")
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Link to scene
    bpy.context.collection.objects.link(obj)
    
    # Create bmesh for easier mesh manipulation
    bm = bmesh.new()
    
    # Add optimized vertices
    vertices = []
    optimized_vertices = compressed_data["vertices"]
    for i in range(0, len(optimized_vertices), 3):
        vert = bm.verts.new((optimized_vertices[i], optimized_vertices[i+1], optimized_vertices[i+2]))
        vertices.append(vert)
    
    # Create edges between consecutive vertices using original point order
    vertex_indices = compressed_data["vertex_indices"]
    for i in range(len(vertex_indices) - 1):
        if vertex_indices[i] < len(vertices) and vertex_indices[i+1] < len(vertices):
            bm.edges.new([vertices[vertex_indices[i]], vertices[vertex_indices[i+1]]])
    
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
            export_normals=True,
            export_smooth_groups=False,  # Simplify output
            export_material_groups=False,  # Don't create separate material groups
            path_mode='COPY'  # Copy textures if any
        )
        
        # Clean up the OBJ file to remove MTL reference if no materials are actually exported
        _cleanup_obj_file(abs_path)
        
        return abs_path
    except AttributeError:
        # Fallback to old API for Blender < 4.4
        try:
            bpy.ops.export_scene.obj(
                filepath=abs_path,
                use_selection=selected_only,
                use_materials=True,
                use_uvs=True,
                use_normals=True,
                use_smooth_groups=False,
                path_mode='COPY'
            )
            
            # Clean up the OBJ file
            _cleanup_obj_file(abs_path)
            
            return abs_path
        except AttributeError:
            # If both fail, try manual export or alternative method
            print(f"Warning: OBJ export not available, saving as .blend instead")
            blend_path = abs_path.replace('.obj', '.blend')
            return save_blend_file(blend_path)

def _cleanup_obj_file(obj_filepath: str):
    """
    Clean up OBJ file to remove MTL references if MTL file doesn't exist or is empty.
    
    Args:
        obj_filepath: Path to the OBJ file
    """
    try:
        # Check if MTL file exists and has content
        mtl_filepath = obj_filepath.replace('.obj', '.mtl')
        mtl_exists = os.path.exists(mtl_filepath)
        mtl_has_content = False
        
        if mtl_exists:
            with open(mtl_filepath, 'r') as f:
                content = f.read().strip()
                # Check if MTL file has actual material definitions
                mtl_has_content = 'newmtl' in content and len(content.split('\n')) > 5
        
        # Read OBJ file
        with open(obj_filepath, 'r') as f:
            lines = f.readlines()
        
        # Filter out MTL-related lines if MTL doesn't exist or is empty
        cleaned_lines = []
        for line in lines:
            line_stripped = line.strip()
            
            if not mtl_has_content:
                # Remove MTL library reference and material usage if no proper MTL
                if line_stripped.startswith('mtllib ') or line_stripped.startswith('usemtl '):
                    continue
            
            cleaned_lines.append(line)
        
        # Write cleaned OBJ file
        with open(obj_filepath, 'w') as f:
            f.writelines(cleaned_lines)
        
        # Remove empty or minimal MTL file
        if mtl_exists and not mtl_has_content:
            try:
                os.remove(mtl_filepath)
                print(f"Removed empty MTL file: {mtl_filepath}")
            except OSError:
                pass
                
    except Exception as e:
        print(f"Warning: Could not clean up OBJ file {obj_filepath}: {e}")

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
    
    # Execute each command using simple parsing
    for cmd_type, cmd_data in commands:
        try:
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
            elif cmd_type == "custom_coords":
                obj_name = draw_custom_mesh_from_coords(
                    parsed_data["coordinates_text"], parsed_data["color"],
                    parsed_data["name"], parsed_data["use_convex_hull"]
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


def optimize_vertices(vertices: List[Tuple[float, float, float]], precision: int = 3) -> List[Tuple[float, float, float]]:
    """
    Legacy function - use optimize_vertices_advanced for better performance.
    """
    unique_vertices, _ = optimize_vertices_advanced(vertices, precision, use_float32=True)
    return unique_vertices


def draw_custom_mesh_from_coords(coordinates_text: str, color: Color, name: str = "CustomMesh", 
                                use_convex_hull: bool = True) -> str:
    """
    Create a custom mesh from coordinate text input with vertex optimization.
    
    Args:
        coordinates_text: Text with coordinates, one vertex per line: "x y z" or "(x y z)"
        color: Mesh color
        name: Object name
        use_convex_hull: Whether to apply convex hull operation
        
    Returns:
        Name of created object
        
    Raises:
        ValueError: If coordinates are invalid
    """
    # Parse coordinates from text
    vertices = []
    for i, line in enumerate(coordinates_text.strip().splitlines()):
        line = line.strip()
        if not line:
            continue
            
        # Remove parentheses if present
        line = line.replace("(", "").replace(")", "")
        parts = line.split()
        
        if len(parts) != 3:
            raise ValueError(f"Line {i+1} must have exactly 3 values (x y z)")
        
        try:
            x, y, z = [float(v) for v in parts]
            vertices.append((x, y, z))
        except ValueError:
            raise ValueError(f"Line {i+1} contains non-numeric values")
    
    if len(vertices) < 3:
        raise ValueError("At least 3 vertices are required")
    
    # Apply advanced vertex optimization
    compressed_data = compress_geometry_data(vertices)
    
    print(f"Custom mesh vertices optimized: {compressed_data['original_vertex_count']} -> {compressed_data['vertex_count']} "
          f"(compression ratio: {compressed_data['compression_ratio']:.3f})")
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    
    # Reconstruct optimized vertices
    optimized_vertices = []
    flattened = compressed_data["vertices"]
    for i in range(0, len(flattened), 3):
        optimized_vertices.append((flattened[i], flattened[i+1], flattened[i+2]))
    
    # Create initial mesh from optimized vertices
    if use_convex_hull:
        # Create bmesh for convex hull operation
        bm = bmesh.new()
        
        # Add optimized vertices to bmesh
        for vertex in optimized_vertices:
            bm.verts.new(vertex)
        
        # Apply convex hull to generate faces
        bmesh.ops.convex_hull(bm, input=bm.verts)
        
        # Update mesh from bmesh
        bm.to_mesh(mesh)
        bm.free()
    else:
        # For simple case without convex hull, create basic triangular faces
        faces = []
        vertex_count = len(optimized_vertices)
        
        if vertex_count >= 4:
            # Create tetrahedron-like faces for 4+ vertices
            faces = [
                [0, 1, 2],
                [0, 2, 3 % vertex_count],
                [0, 3 % vertex_count, 1],
                [1, 2, 3 % vertex_count]
            ]
        elif vertex_count == 3:
            # Single triangle
            faces = [[0, 1, 2]]
        
        # Create mesh from optimized vertices and faces
        mesh.from_pydata(optimized_vertices, [], faces)
    
    mesh.update()
    
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
