import omni
import asyncio
import pxr

import math

from pxr import UsdShade, Sdf


class LooksSuite:
    """
    A set of tools to change materials and update parameters
    """

    def __init__(self):
        print("Initialized Looks Suite.")

    # Change material on select object
    def change_material(self, stage, path, materialname):
        """
        Re-factors the MDL material on the given object.
        Inputs:
            stage: The name of the world the objects belong to.
            path: The name of the object in the world.
            materialname: The name of the material to be applied.
        Outputs:
            None.
        """
        obj = stage.GetPrimAtPath(path)

        mtl_created = []

        # Create the material and place it in the library
        omni.kit.commands.execute(
            "CreateAndBindMdlMaterialFromLibrary",
            mdl_name=materialname + ".mdl",
            mtl_name=materialname,
            mtl_created_list=mtl_created,
        )

        # Get the created material
        mtl_path = mtl_created[0]

        # Bind it to the object of choice
        omni.kit.commands.execute("BindMaterial", prim_path=obj.GetPath(), material_path=mtl_path)

    def bind_material(self, stage, object_path, mat_path):
        mtl_prim = stage.GetPrimAtPath(mat_path)

        # Get the path to the prim
        prim = stage.GetPrimAtPath(object_path)

        # Bind the material to the prim
        prim_mat_shade = UsdShade.Material(mtl_prim)

        UsdShade.MaterialBindingAPI(prim).Bind(prim_mat_shade, UsdShade.Tokens.strongerThanDescendants)

    def unbind_materials(self, stage, path):
        prim = stage.GetPrimAtPath(path)

        if prim.IsValid():
            # Unbind Material.
            UsdShade.MaterialBindingAPI(prim).UnbindAllBindings()

    def get_material(self, stage, path):
        prim = stage.GetPrimAtPath(path)

        # Get Material.
        rel = UsdShade.MaterialBindingAPI(prim).GetDirectBindingRel()
        pathList = rel.GetTargets()

        for mTargetPath in pathList:
            print("  material : " + mTargetPath.pathString)

            material = UsdShade.Material(stage.GetPrimAtPath(mTargetPath))
            print(material)

    def assign_texture_with_normals(self, stage, object_path, material, tex_path, normal_path):
        mtl_prim = stage.GetPrimAtPath(material)

        # Set material inputs, these can be determined by looking at the .mdl file
        # or by selecting the Shader attached to the Material in the stage window and looking at the details panel
        omni.usd.create_material_input(
            mtl_prim,
            "diffuse_texture",
            tex_path,
            Sdf.ValueTypeNames.Asset,
        )

        omni.usd.create_material_input(
            mtl_prim,
            "normalmap_texture",
            normal_path,
            Sdf.ValueTypeNames.Asset,
        )

        # Get the path to the prim
        prim = stage.GetPrimAtPath(object_path)

        # Bind the material to the prim
        prim_mat_shade = UsdShade.Material(mtl_prim)

        UsdShade.MaterialBindingAPI(prim).Bind(prim_mat_shade, UsdShade.Tokens.strongerThanDescendants)

    def modify_float_parameter(self, stage, object_path, mat_path, param_name, param_value):
        mtl_prim = stage.GetPrimAtPath(mat_path)

        omni.usd.create_material_input(
            mtl_prim,
            param_name,
            param_value,
            Sdf.ValueTypeNames.Float,
        )

        # Get the path to the prim
        prim = stage.GetPrimAtPath(object_path)

        # Bind the material to the prim
        prim_mat_shade = UsdShade.Material(mtl_prim)

        UsdShade.MaterialBindingAPI(prim).Bind(prim_mat_shade, UsdShade.Tokens.strongerThanDescendants)
