import omni
import carb
import carb.events
import carb.settings

from omni.kit.viewport.utility import get_active_viewport

import asyncio
import os


class CaptureSuite:
    """Take in-system screenshot with camera and resolution control"""

    def __init__(self):
        print("Initialized Screen Capture Tool.")

    def take_screenshot(
            self,
            img_path="",
            use_custom_camera=False,
            switch_cam=False,
            cam_path="/World/Camera",
            resolution=(1920, 1080),
            rendermode="PathTracing",
            spp=64,
            disable_async=False,
    ):
        # print("Configuring capture settings... ")

        # Create capture path if it doesn't exist
        if not os.path.exists(os.path.dirname(img_path)):
            os.mkdir(os.path.dirname(img_path))

        # Set post-processing effects
        settings = carb.settings.get_settings()

        # Remove Gizmos from RGB
        # settings.set("/persistent/app/viewport/displayOptions", 0)

        # Remove ASYNC rendering to improve rendering stability
        if disable_async:
            settings.set_bool("/app/asyncRendering", False)
            settings.set_bool("/app/asyncRenderingLowLatency", False)

        # Allow interactivity in the UI and accumulation of subframes for motion blur
        settings.set_int("/rtx/pathtracing/spp", 1)

        # Enable syncLoads in materialDB and Hydra. This is needed to make sure texture updates finish before we start the rendering
        settings.set("/rtx/materialDb/syncLoads", True)
        settings.set("/rtx/hydra/materialSyncLoads", True)

        if settings.get("/rtx/rendermode") != rendermode:
            # Set to PathTraced rendering by default
            settings.set("/rtx/rendermode", rendermode)
            settings.set("/rtx/pathtracing/totalSpp", spp)

            print("Switching to PathTracing")

        # print("Acquiring viewport interface... ")

        # Get main viewport and renderer
        # viewport_interface = omni.kit.viewport.acquire_viewport_interface()
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # renderer = omni.renderer_capture.acquire_renderer_capture_interface()

        # Get active viewport window and set the texture accordingly
        viewport_window = get_active_viewport()
        # viewport_window.set_texture_resolution(resolution[0], resolution[1])

        # Get viewport image.
        # viewport_ldr = viewport_window.get_drawable_ldr_resource()

        # OPTIONAL: Set active camera
        if use_custom_camera:
            print("Setting render camera... ")
            viewport_window.set_active_camera(cam_path)
        elif switch_cam:
            print("Setting render camera... ")
            # If no camera is set, go for the default Omniverse camera
            viewport_window.set_active_camera("/OmniverseKit_Persp")

        # Set the final image resolution
        viewport_window.set_texture_resolution(resolution)

        # Get viewport image.
        # viewport_ldr = viewport_window.get_drawable_ldr_resource()

        # print("Say cheese!")

        # Get renderer and render image
        # renderer.capture_next_frame_rp_resource(img_path, viewport_ldr)
        omni.kit.viewport.utility.capture_viewport_to_file(file_path=img_path, viewport_api=viewport_window)

    async def take_screenshot_async(
            self,
            img_path="",
            use_custom_camera=False,
            switch_cam=False,
            cam_path="/World/Camera",
            resolution=(1920, 1080),
            rendermode="PathTracing",
            spp=64,
            disable_async=False,
    ):
        await omni.kit.app.get_app().next_update_async()
        self.take_screenshot(
            img_path, use_custom_camera, switch_cam, cam_path, resolution, rendermode, spp, disable_async=disable_async
        )

    async def take_screenshot_legacy(
            self, img_path="", use_custom_camera=False, cam_path="/World/Camera", resolution=(1920, 1080),
            capture_delay=5
    ):
        print("Capturing screen... ")

        # Test 2: Capture screen (IT WORKS!)
        renderer = omni.renderer_capture.acquire_renderer_capture_interface()
        viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()

        viewport_window = viewport_interface.get_viewport_window()
        viewport_window.set_texture_resolution(resolution[0], resolution[1])

        # OPTIONAL: Set active camera
        if use_custom_camera:
            viewport_window.set_active_camera(cam_path)
            # viewport_window.set_camera_position(camera_path, camera_pos[0], camera_pos[1], camera_pos[2], True)
            # viewport_window.set_camera_target(camera_path, camera_rot[0], camera_rot[1], camera_rot[2], True)
        else:
            # If no camera is set, go for the default Omniverse camera
            viewport_window.set_active_camera("/OmniverseKit_Persp")

        # Time buffer to execute camera change
        await asyncio.sleep(capture_delay)

        # Capture object
        def _capture_helper(viewport_rp_resource):
            renderer.capture_next_frame_rp_resource(str(img_path), viewport_rp_resource)

        omni.kit.viewport_legacy.deferred_capture(
            viewport_window, _capture_helper, subscription_name="omni.kit.capture capture helper"
        )
