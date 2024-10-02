import omni
import asyncio

import omni.timeline

from pxr import Usd, UsdGeom, Gf


class MovementSuite:
    def __init__(self):
        pass

    # Do ANY form of object positional/rotational transformation here
    def move_object_timeline(
        self, stage, object_path, keyframe, location=Gf.Vec3d(0, 0, 0), rotation=Gf.Quaternion(1, Gf.Vec3d(0, 0, 0))
    ):
        obj = stage.GetPrimAtPath(object_path)

        # Use USD Geometric tools to translate/rotate the object

        # print("Performing translation... ")
        UsdGeom.XformCommonAPI(obj).SetRotate(rotation, keyframe)
        UsdGeom.XformCommonAPI(obj).SetTranslate(location, keyframe)

    def set_point_on_timeline(self, timeframe, fps, auto_update=False):
        omni.timeline.get_timeline_interface().set_auto_update(auto_update)
        omni.timeline.get_timeline_interface().set_current_time(timeframe / fps)

    def get_current_point_on_timeline(self, stage):
        # Get the current time on the timeline
        return omni.timeline.get_timeline_interface().get_current_time() * stage.GetTimeCodesPerSecond()

    def get_timeline_without_timecode(self):
        return omni.timeline.get_timeline_interface().get_current_time()

    def get_end_time(self):
        return omni.timeline.get_timeline_interface().get_end_time()

    def get_end_timecode(self, stage):
        return stage.GetEndTimeCode()

    def pause_timeline(self):
        omni.timeline.get_timeline_interface().pause()

    def play_timeline(self):
        omni.timeline.get_timeline_interface().play()

    def freemove_object(self):
        # TODO: Research exercise; identify movement without touching the timeline
        # Current indication: Use PhysX to adjust simulation

        # # Begin movement simulation
        # get_physx_interface().start_simulation()

        # # Update to next timestamp
        # get_physx_interface().update_simulation(dt, currentTime)
        # # Update transformations made to prims
        # get_physx_interface().update_transformations(False, True)

        # # (Once simulation is completed) Reset the full transformation
        # get_physx_interface().reset_simulation()
        pass
