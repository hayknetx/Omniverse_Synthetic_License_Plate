import omni
import carb
import asyncio

import omni.kit.asset_converter


class StageSuite:
    def __init__(self):
        print("Initiated Stage Tools.")

    # OBJ/STL/FBX/etc to USD
    async def convert_asset_to_usd(
        self,
        input_obj: str,
        output_usd: str,
        ignore_material=False,
        ignore_animation=False,
        ignore_cameras=True,
        single_mesh=True,
        smooth_normals=True,
        preview_surface=False,
        support_point_instancer=False,
        embed_mdl_in_usd=False,
        use_meter_as_world_unit=True,
        create_world_as_default_root_prim=False,
    ):
        def progress_callback(progress, total_steps):
            pass

        converter_context = omni.kit.asset_converter.AssetConverterContext()
        # setup converter and flags
        converter_context.ignore_material = ignore_material
        converter_context.ignore_animation = ignore_animation
        converter_context.ignore_cameras = ignore_cameras
        converter_context.single_mesh = single_mesh
        converter_context.smooth_normals = smooth_normals
        converter_context.preview_surface = preview_surface
        converter_context.support_point_instancer = support_point_instancer
        converter_context.embed_mdl_in_usd = embed_mdl_in_usd
        converter_context.use_meter_as_world_unit = use_meter_as_world_unit
        converter_context.create_world_as_default_root_prim = create_world_as_default_root_prim

        instance = omni.kit.asset_converter.get_instance()
        task = instance.create_converter_task(input_obj, output_usd, progress_callback, converter_context)
        success = await task.wait_until_finished()

        if not success:
            carb.log_error(task.get_status(), task.get_detailed_error())

        print("Conversion to USD Complete.")


    def save_scene(self, nucleus_server="/create/nucleus/default", save_path="/Users/test/saved.usd"):
        # Change server below to your nucleus install
        default_server = carb.settings.get_settings().get(nucleus_server)
        
        # Change the path as needed
        omni.usd.get_context().save_as_stage(default_server + save_path, None)
