import omni
import asyncio

from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window, get_active_viewport_and_window

from pxr import Usd, UsdGeom, Gf, CameraUtil
import math


class CameraSuite:
    """
    A set of tools to create, move, configure, and manipulate cameras
    """

    def __init__(self):
        print("Initialized Camera Suite.")

    def create_camera(
        self,
        stage=None,
        cam_path="/World/Camera",
        resolution=(1920, 1080),
        fov=110.0,
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
    ):
        # Create camera
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()

        viewport_window = get_active_viewport()

        # Instantiate Camera
        camera_prim = stage.DefinePrim(str(cam_path), "Camera")

        # Set Camera properties: FOV, Resolution, Position, Rotation
        focal_length = camera_prim.GetAttribute("focalLength")
        focal_length.Set(fov)

        viewport_window.set_active_camera(cam_path)
        viewport_window.set_texture_resolution(resolution)
        viewport_window.set_camera_position(cam_path, position[0], position[1], position[2], True)
        viewport_window.set_camera_target(cam_path, rotation[0], rotation[1], rotation[2], True)

        return camera_prim

    def switch_camera(self, camera_path):
        # Create camera
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()

        viewport_window = get_active_viewport()

        viewport_window.set_active_camera(camera_path)

    def get_current_cam(self):
        # Get main window viewport. (raw)
        # viewportI = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewportI.get_viewport_window(None)
        viewport_window = get_active_viewport()

        # Get current camera
        current_cam = viewport_window.get_active_camera()

        return current_cam

    def config_camera(
        self,
        stage=None,
        cam_path="/World/Camera",
        resolution=(1920, 1080),
        fov=110.0,
        position=(0.0, 0.0, 0.0),
        rotation=(0.0, 0.0, 0.0),
    ):

        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()

        viewport_window = get_active_viewport()

        # Set Camera properties: FOV, Resolution, Position, Rotation
        cam_prim = stage.GetPrimAtPath(cam_path)
        focal_length = cam_prim.GetAttribute("focalLength")
        focal_length.Set(fov)

        viewport_window.set_active_camera(cam_path)
        viewport_window.set_texture_resolution(resolution)
        viewport_window.set_camera_position(cam_path, position[0], position[1], position[2], True)
        viewport_window.set_camera_target(cam_path, rotation[0], rotation[1], rotation[2], True)

    def set_fov(self, stage=None, cam_path="/World/Camera", fov=110.0):
        # Set Camera properties: FOV
        cam_prim = stage.GetPrimAtPath(cam_path)
        focal_length = cam_prim.GetAttribute("focalLength")
        focal_length.Set(fov)

    def get_fov(self, stage=None, cam_path="/World/Camera"):
        cam_prim = stage.GetPrimAtPath(cam_path)
        focal_length = cam_prim.GetAttribute("focalLength")
        return focal_length.Get()

    def set_resolution(self, resolution=(1920, 1080)):
        # Set Camera properties: Resolution
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()
        viewport_window = get_active_viewport()
        viewport_window.set_texture_resolution(resolution)

    def set_position(self, cam_path="/World/Camera", position=(0.0, 0.0, 0.0)):
        # Set Camera properties: Position
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()
        viewport_window = get_active_viewport()
        viewport_window.set_camera_position(cam_path, position[0], position[1], position[2], True)

    def get_position(self, stage=None, cam_path="/World/Camera"):
        time_code = Usd.TimeCode.Default()

        # Get active camera.
        cameraPrim = stage.GetPrimAtPath(cam_path)

        if cameraPrim.IsValid():
            camera = UsdGeom.Camera(cameraPrim)  # UsdGeom.Camera
            cameraV = camera.GetCamera(time_code)  # Gf.Camera

            viewInv = cameraV.frustum.ComputeViewMatrix().GetInverse()

            # Camera position(World).
            return viewInv.Transform(Gf.Vec3f(0, 0, 0))

    def set_rotation(self, cam_path="/World/Camera", rotation=(0.0, 0.0, 0.0)):
        # Set Camera properties: Position
        # viewport_interface = omni.kit.viewport_legacy.acquire_viewport_interface()
        # viewport_window = viewport_interface.get_viewport_window()
        viewport_window = get_active_viewport()
        viewport_window.set_camera_target(cam_path, rotation[0], rotation[1], rotation[2], True)

    def get_world_to_camera_matrix(self, stage, cam_path):
        cam_prim = stage.GetPrimAtPath(cam_path)

        if cam_prim.IsValid():
            time_code = Usd.TimeCode.Default()

            # Fetch Camera as Gf.Camera
            cameraV = UsdGeom.Camera(cam_prim).GetCamera(time_code)

        cv = CameraUtil.ScreenWindowParameters(cameraV)

        # This is the world-to-camera matrix
        world_to_cam = cameraV.frustum.ComputeViewMatrix().GetInverse()

        return world_to_cam


    def point_to_pixel(self, stage, cam, world_coord, resolution=(1920, 1080)):
        viewport_window = get_active_viewport_window()

        if hasattr(viewport_window, "legacy_window"):
            return self.point_to_pixel_legacy(stage, cam, world_coord, resolution=(1920, 1080))
        else:
            return self.point_to_pixel_new(stage, cam, world_coord, resolution)


    def point_to_pixel_new(self, stage, cam, world_coord, resolution=(1920, 1080)):
        time_code = Usd.TimeCode.Default()

        # Get DPI for correct scaling
        dpi = omni.ui.Workspace.get_dpi_scale()
        if dpi <= 0.0:
            dpi = 1

        # Get active Viewport
        viewport_window = get_active_viewport_window()
        
        # Get the current rendering camera
        cameraPrim = stage.GetPrimAtPath(cam)
        if cameraPrim.IsValid() == False:
            return

        # Get camera matrix.
        camera = UsdGeom.Camera(cameraPrim)  # Geom.Camera
        cameraV = camera.GetCamera(time_code)  # Gf.Camera
        frustum = cameraV.frustum
        viewMatrix = frustum.ComputeViewMatrix()
        projectionMatrix = frustum.ComputeProjectionMatrix()

        # AspectRatio.
        cameraAspect = cameraV.aspectRatio

        # ray.direction to screen pos
        vPos = viewMatrix.Transform(world_coord)

        # screen position : -1.0 to +1.0; Depending on the aspect ratio, the value may be greater than 1.0.
        sPos = projectionMatrix.Transform(vPos)

        frame = viewport_window.frame
        viewportSize = [frame.computed_width, frame.computed_height]

        aspect = viewportSize[0] / viewportSize[1]

        # Calculate position within viewport
        sx = viewportSize[0] * 0.5 * (1.0 + sPos[0])
        sy = viewportSize[1] * 0.5 * (1.0 - sPos[1] / (cameraAspect / aspect))

        # Scale the coordinates w.r.t image resolution
        cam_x = dpi * (sx / (viewportSize[0])) * resolution[0]
        cam_y = dpi * (sy / (viewportSize[1])) * resolution[1]

        # Clip coordinates to be able to draw proper bounding boxes
        if cam_x < 0:
            cam_x = 0
        elif cam_x > resolution[0]:
            cam_x = resolution[0]

        if cam_y < 0:
            cam_y = 0
        elif cam_y > resolution[1]:
            cam_y = resolution[1]

        return cam_x, cam_y

    def point_to_pixel_legacy(self, stage, cam, world_coord, resolution=(1920, 1080)):
        time_code = Usd.TimeCode.Default()

        # Get Viewport
        # viewportI = omni.kit.viewport_legacy.acquire_viewport_interface()
        # vWindow = viewportI.get_viewport_window(None)

        viewport_window = get_active_viewport()

        # Get viewport rect.
        viewportRect = viewport_window.legacy_window.get_viewport_rect()
        viewportSize = (viewportRect[2] - viewportRect[0], viewportRect[3] - viewportRect[1])

        cameraPrim = stage.GetPrimAtPath(cam)
        if cameraPrim.IsValid() == False:
            return

        # Get camera matrix.
        camera = UsdGeom.Camera(cameraPrim)  # Geom.Camera
        cameraV = camera.GetCamera(time_code)  # Gf.Camera
        frustum = cameraV.frustum
        viewMatrix = frustum.ComputeViewMatrix()
        projectionMatrix = frustum.ComputeProjectionMatrix()

        # AspectRatio.
        cameraAspect = cameraV.aspectRatio

        # ray.direction to screen pos
        vPos = viewMatrix.Transform(world_coord)

        # screen position : -1.0 to +1.0; Depending on the aspect ratio, the value may be greater than 1.0.
        sPos = projectionMatrix.Transform(vPos)

        aspect = viewportSize[0] / viewportSize[1]

        # Calculate position within viewport
        sx = viewportSize[0] * 0.5 * (1.0 + sPos[0])
        sy = viewportSize[1] * 0.5 * (1.0 - sPos[1] / (cameraAspect / aspect))

        # Scale the coordinates w.r.t image resolution
        cam_x = (sx / (viewportSize[0])) * resolution[0]
        cam_y = (sy / (viewportSize[1])) * resolution[1]

        # Clip coordinates to be able to draw proper bounding boxes
        if cam_x < 0:
            cam_x = 0
        elif cam_x > resolution[0]:
            cam_x = resolution[0]

        if cam_y < 0:
            cam_y = 0
        elif cam_y > resolution[1]:
            cam_y = resolution[1]

        return cam_x, cam_y

    def compute_distance_from_cam(self, stage, cam_path, coord):
        cam_pos = self.get_position(stage, cam_path)

        # Euclidean distance between cam & LP
        dist = math.sqrt(
            math.pow(coord[0] - cam_pos[0], 2) + math.pow(coord[1] - cam_pos[1], 2) + math.pow(coord[2] - cam_pos[2], 2)
        )

        return dist

    def is_in_cam_view(self, stage, cam_path, bbox):
        cam_prim = stage.GetPrimAtPath(cam_path)

        if cam_prim.IsValid():
            time_code = Usd.TimeCode.Default()

            # Fetch Camera as Gf.Camera
            cameraV = UsdGeom.Camera(cam_prim).GetCamera(time_code)

        # Check if bounding box is within the viewing range of the given camera
        return cameraV.frustum.Intersects(bbox)

    def calculate_focal_point_and_center(self, stage, camera, resolution=(1920, 1080)):
        width = resolution[0]
        height = resolution[1]

        aspect_ratio = width / height

        # get camera prim attached to viewport
        camera = stage.GetPrimAtPath(camera)
        focal_length = camera.GetAttribute("focalLength").Get()
        horiz_aperture = camera.GetAttribute("horizontalAperture").Get()
        vert_aperture = camera.GetAttribute("verticalAperture").Get()
        # Pixels are square so we can also do:
        # vert_aperture = height / width * horiz_aperture
        near, far = camera.GetAttribute("clippingRange").Get()
        fov = 2 * math.atan(horiz_aperture / (2 * focal_length))

        # helper to compute projection matrix
        # proj_mat = helpers.get_projection_matrix(fov, aspect_ratio, near, far)

        # compute focal point and center
        focal_x = height * focal_length / vert_aperture
        focal_y = width * focal_length / horiz_aperture
        center_x = height * 0.5
        center_y = width * 0.5

        return focal_x, focal_y, center_x, center_y

    def get_details(self, stage, cam_path):
        cam_prim = stage.GetPrimAtPath(cam_path)

        if cam_prim.IsValid():
            time_code = Usd.TimeCode.Default()

            # Fetch Camera as Gf.Camera
            cameraV = UsdGeom.Camera(cam_prim).GetCamera(time_code)

            print("Aspect : " + str(cameraV.aspectRatio))
            print("fov(H) : " + str(cameraV.GetFieldOfView(Gf.Camera.FOVHorizontal)))
            print("fov(V) : " + str(cameraV.GetFieldOfView(Gf.Camera.FOVVertical)))
            print("FocalLength : " + str(cameraV.focalLength))
            print("World to camera matrix : " + str(cameraV.transform))

            viewMatrix = cameraV.frustum.ComputeViewMatrix()
            print("View matrix : " + str(viewMatrix))

            viewInv = viewMatrix.GetInverse()

            # Camera position(World).
            cameraPos = viewInv.Transform(Gf.Vec3f(0, 0, 0))
            print("Camera position(World) : " + str(cameraPos))

            # Camera vector(World).
            cameraVector = viewInv.TransformDir(Gf.Vec3f(0, 0, -1))
            print("Camera vector(World) : " + str(cameraVector))

            projectionMatrix = cameraV.frustum.ComputeProjectionMatrix()
            print("Projection matrix : " + str(projectionMatrix))
