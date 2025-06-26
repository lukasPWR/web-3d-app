"""
Blender script for updating existing .obj models with new transforms and material properties.
Based on the provided template script for handling position, rotation, scale and material updates.
"""

import bpy
import sys
import json
import argparse
from pathlib import Path


def parse_args():
    """
    Parse arguments after `--`:
      --input   json with update data (string or file)
      --obj     path to original .obj file to load
      --output  path to save updated .obj file
    """
    parser = argparse.ArgumentParser(description="Update object transforms & material")
    parser.add_argument("--input", type=str, required=True,
                        help="JSON string or path to .json file with update spec")
    parser.add_argument("--obj", type=str, required=True,
                        help="Path to original .obj file to load")
    parser.add_argument("--output", type=str, required=True,
                        help="Path to save updated .obj file")
    args, unknown = parser.parse_known_args(sys.argv[sys.argv.index("--")+1:])
    return args


def clear_scene():
    """Clear all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def load_obj_file(obj_path):
    """Load OBJ file into Blender scene."""
    clear_scene()
    
    # Import OBJ file
    bpy.ops.wm.obj_import(filepath=obj_path)
    
    # Get the imported object (should be the only one now)
    if bpy.context.selected_objects:
        return bpy.context.selected_objects[0]
    else:
        # If no selected objects, get the first mesh object
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                return obj
    
    raise ValueError(f"No mesh object found after importing {obj_path}")


def apply_updates(obj, spec):
    """
    Apply updates to object based on specification.
    
    spec = {
      "location": [x,y,z],
      "rotation": [rx,ry,rz],      # Euler in radians
      "scale":    [sx,sy,sz],
      "material": {
         "color":      [r,g,b,a],  # rgba 0..1
         "roughness":  float,
         "metallic":   float,
         "emission":   [r,g,b],
         "emissiveIntensity": float
      }
    }
    """
    # TRANSFORMS
    if "location" in spec:
        obj.location = spec["location"]
    
    if "rotation" in spec:
        obj.rotation_mode = 'XYZ'
        # Convert from degrees to radians if needed
        rotation = spec["rotation"]
        if all(abs(r) > 6.28 for r in rotation):  # Likely in degrees
            rotation = [r * 3.14159 / 180 for r in rotation]
        obj.rotation_euler = rotation
    
    if "scale" in spec:
        obj.scale = spec["scale"]
    
    # MATERIAL
    mat_spec = spec.get("material")
    if mat_spec is not None:
        # Get or create first material of object
        if obj.data.materials:
            mat = obj.data.materials[0]
        else:
            mat = bpy.data.materials.new(name=f"{obj.name}_material")
            obj.data.materials.append(mat)
        
        # Enable material nodes
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        
        if not bsdf:
            # Create Principled BSDF if it doesn't exist
            bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
            output = nodes.get("Material Output")
            if output:
                mat.node_tree.links.new(bsdf.outputs[0], output.inputs[0])
        
        # Apply material properties
        if "color" in mat_spec:
            col = mat_spec["color"]
            if len(col) == 3:
                col = col + [1.0]  # Add alpha if missing
            bsdf.inputs["Base Color"].default_value = col
        
        if "roughness" in mat_spec:
            bsdf.inputs["Roughness"].default_value = mat_spec["roughness"]
        
        if "metallic" in mat_spec:
            bsdf.inputs["Metallic"].default_value = mat_spec["metallic"]
        
        if "emission" in mat_spec:
            em = mat_spec["emission"]
            if len(em) == 3:
                em = em + [1.0]  # Add alpha if missing
            bsdf.inputs["Emission"].default_value = em
        
        if "emissiveIntensity" in mat_spec:
            # In newer Blender versions, use Emission Strength
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = mat_spec["emissiveIntensity"]


def export_obj_with_materials(obj, output_path):
    """Export object to OBJ format with MTL file."""
    # Select only our object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Export to OBJ
    output_path = Path(output_path)
    bpy.ops.wm.obj_export(
        filepath=str(output_path),
        export_selected_objects=True,
        export_materials=True,
        export_uv=True,
        export_normals=True,
        export_smooth_groups=True,
        smooth_group_bitflags=False
    )


def main():
    """Main function to process object updates."""
    try:
        args = parse_args()
        
        # Load update specification
        try:
            # Try to load as file first
            with open(args.input, 'r') as f:
                spec = json.load(f)
        except FileNotFoundError:
            # Treat as literal JSON string
            spec = json.loads(args.input)
        
        print(f"[INFO] Loading OBJ file: {args.obj}")
        print(f"[INFO] Update specification: {json.dumps(spec, indent=2)}")
        
        # Load the original OBJ file
        obj = load_obj_file(args.obj)
        print(f"[INFO] Loaded object: {obj.name}")
        
        # Apply updates
        apply_updates(obj, spec)
        print(f"[INFO] Applied updates to object")
        
        # Export updated model
        export_obj_with_materials(obj, args.output)
        print(f"[INFO] Exported updated model to: {args.output}")
        
        # Also export MTL file path for reference
        mtl_path = Path(args.output).with_suffix('.mtl')
        print(f"[INFO] MTL file created at: {mtl_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to update model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
