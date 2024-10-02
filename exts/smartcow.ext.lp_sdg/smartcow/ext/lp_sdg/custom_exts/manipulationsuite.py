import omni
from pxr import Usd, UsdGeom, Gf

import numpy as np


class ManipulationSuite:
    """
    All object manipulation capabilities that can be used within a scene.
    """

    def __init__(self):
        print("Initialized Manipulation Tool.")

    def create_prim(self, stage, path, prim_type="Cube"):
        """
        Creates a standard 3D object from the Omniverse mesh suite
        Inputs:
            stage: The name of the world the objects belong to.
            path: The path of to the USD file on the docker/drive.
            prim_type: The name of the primitive to spawn
        Output:
            prim: The generated primitive
        """
        # Instantiate Basic Prim
        prim = stage.DefinePrim(str(path), prim_type)

        return prim

    # Spawn Object from USD file
    def create_object(self, stage, prefix, path, position=(0, 0, 0), rotation=(0, 0, 0), group=[]):
        """
        Creates a 3D object from a USD file and adds it into the scene with a given rotation and location
        Inputs:
            prefix: The name of the object in the world (does not have to be unique).
            stage: The name of the world the objects belong to.
            path: The path of to the USD file on the docker/drive.
            location: The position of the object relatively to the stage.
            rotation: The rotation of the object relatively to the stage.
            group: The group of primitives this object belongs to.
        Outputs:
            group: The group of primitives this object belongs to.
        """

        # Get stage
        prim_path = omni.usd.get_stage_next_free_path(stage, prefix, False)
        group.append(prim_path)
        # Get/Create XFORM of object
        tile_prim = stage.DefinePrim(prim_path, "Xform")
        tile_prim.GetReferences().AddReference(path)
        xform = UsdGeom.Xformable(tile_prim)
        # Set translation
        xform_op = xform.AddXformOp(UsdGeom.XformOp.TypeTransform, UsdGeom.XformOp.PrecisionDouble, "")
        mat = Gf.Matrix4d().SetTranslate(Gf.Vec3d(position))
        # Set rotation
        mat.SetRotateOnly(Gf.Rotation(Gf.Quaternion(1, Gf.Vec3d(rotation))))
        xform_op.Set(mat)

        return tile_prim

    #######################################
    ## TRANSFORMATIONS GET/SET FUNCTIONS ##
    #######################################

    def get_transformation(self, stage, object_path):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            return prim.GetAttribute("xformOpOrder").Get()

    def set_transformation(self, stage, object_path, new_transform):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            return prim.GetAttribute("xformOpOrder").Set(new_transform)

    def get_translation(self, stage, object_path):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            return prim.GetAttribute("xformOp:translate").Get()

    def set_translation(self, stage, object_path, new_translation):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            trans = prim.GetAttribute("xformOp:translate").Get()

            if trans != None:
                # Specify a value for each type.
                if type(trans) == Gf.Vec3f:
                    prim.GetAttribute("xformOp:translate").Set(Gf.Vec3f(new_translation))
                elif type(trans) == Gf.Vec3d:
                    prim.GetAttribute("xformOp:translate").Set(Gf.Vec3d(new_translation))
            else:
                # xformOpOrder is also updated.
                xformAPI = UsdGeom.XformCommonAPI(prim)
                xformAPI.SetTranslate(Gf.Vec3d(new_translation))

    def get_rotation(self, stage, object_path):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            xformAPI = UsdGeom.XformCommonAPI(prim)
            time_code = Usd.TimeCode.Default()
            _, _, _, _, rotOrder = xformAPI.GetXformVectors(time_code)

            # Convert rotOrder to "xformOp:rotateXYZ" etc.
            t = xformAPI.ConvertRotationOrderToOpType(rotOrder)
            rotateAttrName = "xformOp:" + UsdGeom.XformOp.GetOpTypeToken(t)

            # Set rotate.
            rotate = prim.GetAttribute(rotateAttrName).Get()

            return rotate

    def set_rotation(self, stage, object_path, new_rotation):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            xformAPI = UsdGeom.XformCommonAPI(prim)
            time_code = Usd.TimeCode.Default()
            _, _, _, _, rotOrder = xformAPI.GetXformVectors(time_code)

            # Convert rotOrder to "xformOp:rotateXYZ" etc.
            t = xformAPI.ConvertRotationOrderToOpType(rotOrder)
            rotateAttrName = "xformOp:" + UsdGeom.XformOp.GetOpTypeToken(t)

            # Set rotate.
            rotate = prim.GetAttribute(rotateAttrName).Get()

            if rotate != None:
                # Specify a value for each type.
                if type(rotate) == Gf.Vec3f:
                    prim.GetAttribute(rotateAttrName).Set(Gf.Vec3f(new_rotation))
                elif type(rotate) == Gf.Vec3d:
                    prim.GetAttribute(rotateAttrName).Set(Gf.Vec3d(new_rotation))
            else:
                # xformOpOrder is also updated.
                xformAPI.SetRotate(Gf.Vec3f(new_rotation), rotOrder)

    def get_scale(self, stage, object_path):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            return prim.GetAttribute("xformOp:scale").Get()

    def set_scale(self, stage, object_path, new_scale):
        prim = stage.GetPrimAtPath(object_path)

        if prim.IsValid() == True:
            scale = prim.GetAttribute("xformOp:scale").Get()

            if scale != None:
                # Specify a value for each type.
                if type(scale) == Gf.Vec3f:
                    prim.GetAttribute("xformOp:scale").Set(Gf.Vec3f(new_scale))
                elif type(scale) == Gf.Vec3d:
                    prim.GetAttribute("xformOp:scale").Set(Gf.Vec3d(new_scale))
            else:
                # xformOpOrder is also updated.
                xformAPI = UsdGeom.XformCommonAPI(prim)
                xformAPI.SetScale(Gf.Vec3f(new_scale))

    ##################################
    ## SCENE MANIPULATION FUNCTIONS ##
    ##################################

    # ADJUST WHETHER AN OBJECT IS VISIBLE OR NOT
    def toggle_visibility(self, stage, object_path, is_visible=False):
        prim = stage.GetPrimAtPath(object_path)

        if is_visible:
            prim.GetAttribute("visibility").Set("inherited")
        elif not is_visible:
            prim.GetAttribute("visibility").Set("invisible")

    # DELETION OF PRIMS WITHIN THE OMNIVERSE SCENE
    def delete_object(self, stage, object):
        """
        Deletes a selected object from the given scene.
        Inputs:
            stage: The name of the world the objects belong to.
            object: The name of the usd/primitive to remove from the scene.
        Outputs:
            None.
        """
        path = object.GetPath()
        stage.RemovePrim(path)

    def calculate_bbox(self, stage, object_path, local=False, isRange=True, return_raw=False):
        # Get object at path
        prim = stage.GetPrimAtPath(object_path)

        # Fetch bounding box coordinates from the primitive
        # bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), includedPurposes=[UsdGeom.Tokens.default_])
        bbox_cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "render"])
        bbox_cache.Clear()

        prim_bbox = None
        aligned_bbox = None

        # Calculate Local or World bounding Boxes
        if local:
            prim_bbox = bbox_cache.ComputeLocalBound(prim)
        else:
            prim_bbox = bbox_cache.ComputeWorldBound(prim)

        if isRange:
            # Get Bounding Box with applied transformation matrix for fully correct Range
            aligned_bbox = prim_bbox.ComputeAlignedRange()
        else:
            # Get Bounding Box with applied transformation matrix for fully correct bbox
            aligned_bbox = prim_bbox.ComputeAlignedBox()

        if return_raw:
            return prim_bbox, aligned_bbox
        else:
            return aligned_bbox

    def visualize_bboxes_points(self, stage, bbox, spawnpath, prim_path):
        # Draw spheres @ BBOX coords as visual confirmation
        [
            self.create_object(
                stage,
                spawnpath,
                prim_path,
                position=(
                    np.array(bbox.GetCorner(i))[0],
                    np.array(bbox.GetCorner(i))[1],
                    np.array(bbox.GetCorner(i))[2],
                ),
            )
            for i in range(8)
        ]

    def extract_bbox2D(self, coords):
        # Map 3D coordinates into a 2D Bounding Box in the image
        coords = np.array(coords)

        # Set bounding box to be the minimum and maximum values of X and Y respectively
        x1 = np.floor(np.min(coords[:, 0]))
        x2 = np.floor(np.max(coords[:, 0]))
        y1 = np.floor(np.min(coords[:, 1]))
        y2 = np.floor(np.max(coords[:, 1]))

        return x1, x2, y1, y2
