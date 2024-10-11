from pickle import FALSE
from random import random
from typing import Optional, List
import omni

import omni.kit
import omni.kit.app
import omni.ext
import omni.usd
import omni.ui as ui
import omni.kit.commands
import omni.timeline

# Carb imports
import carb.events
import carb.settings

# Non-Omniverse Packages
import asyncio
import os
import sys
import pathlib
from pathlib import Path

# from elasticsearch import Elasticsearch
import numpy as np
import pandas as pd

from smartcow.ext.lp_sdg.custom_exts.capturesuite import CaptureSuite
from smartcow.ext.lp_sdg.custom_exts.weathersuite import WeatherSuite
from smartcow.ext.lp_sdg.custom_exts.manipulationsuite import ManipulationSuite
from smartcow.ext.lp_sdg.custom_exts.looksuite import LooksSuite
from smartcow.ext.lp_sdg.custom_exts.movementsuite import MovementSuite
from smartcow.ext.lp_sdg.custom_exts.camerasuite import CameraSuite

from smartcow.ext.lp_sdg.custom_exts.indianplategensuite import IndianLicensePlateGenerator
from tqdm import tqdm

from .settings import (
    DT_SCENE_DIRECTORY,
    FPS,
    RESOLUTION,
    SDG_SAMPLES,
    RENDERMODE,
    SPP,
    LAT,
    LON,
    VEHICLES_PATH,
    CAM_PATH,
    LIGHTS_PATH,
    MATERIALS_PATH,
    FONT_PATH,
    RTO_DATA_PATH,
    PLATE_TEX_PATH,
    SAVE_DIR,
    STRF_DATE,
    STRF_DATETIME,
)


################
## MAIN CLASS ##
################


class LP_SDG_Control_Panel:
    """Entrypoint for LP-SDG"""

    def __init__(self):
        """
        All attributes which need to be configured at startup go here
        """

        ###############
        ## CONSTANTS ##
        ###############

        # Get path to extension
        ext_path = pathlib.Path(omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__))

        self.EXTENSION_FILE_PATH = [i for i in ext_path.rglob("extension.py")][0]

        # Get the 'parent' path of the path where the extension can be found; this is our directory
        self.EXTENSION_FOLDER_PATH = self.EXTENSION_FILE_PATH.parent

        # The current context
        self.STAGE = omni.usd.get_context().get_stage()

        # Get SELECTION in viewport
        self.SELECTION = omni.usd.get_context().get_selection()

        # Register all pre-defined settings!
        self.__scene_dir = DT_SCENE_DIRECTORY
        self.__fps = FPS
        self.__resolution = RESOLUTION
        self.__sdg_samples = SDG_SAMPLES
        self.__rendermode = RENDERMODE
        self.__spp = SPP
        self.__lat = LAT
        self.__lon = LON
        self.__vehicles_path = VEHICLES_PATH
        self.__cam_path = CAM_PATH
        self.__lights_path = LIGHTS_PATH
        self.__materials_path = MATERIALS_PATH
        self.__font_path = FONT_PATH
        self.__rto_data_path = RTO_DATA_PATH
        self.__plate_tex_path = PLATE_TEX_PATH
        self.__save_dir = str(pathlib.Path(self.EXTENSION_FOLDER_PATH, SAVE_DIR))
        self.__strf_date = STRF_DATE
        self.__strf_datetime = STRF_DATETIME

        ###################
        ## FUNCTION VARS ##
        ###################

        self.settings = carb.settings.get_settings()

        # All 'game' objects
        self.VEHICLES = []
        self.CAMERAS = []
        self.LIGHTS = []

        # The derived names (+ defaults)
        self.VEHICLE_NAMES = ["Vehicle 1", "Vehicle 2", "Vehicle 3", "Vehicle 4", "Vehicle 5", "Vehicle 6"]
        self.CAMERA_NAMES = ["Camera 1", "Camera 2", "Camera 3", "Camera 4", "Camera 5", "Camera 6"]
        self.LIGHT_NAMES = ["Lights"]

        # Font handling
        self.FONT_LIST = []

        # SYNTHETIC DATA SAVE LOCATIONS: DATA AND IMAGES
        self.IM_PATH = pathlib.Path(self.__save_dir, "snapshots")
        self.DATA_PATH = pathlib.Path(self.__save_dir, "data")

        # LP GENERATION SETTINGS
        self.__bluriness = 0
        self.__font_size = 84
        self.__randomize_font = True

        # Materials location for LP in scene: ADJUST!
        self.ARM_BG_MAT = self.__materials_path + "Arm_Material"
        self.ARM_MIL_BG_MAT = self.__materials_path + "ArmMil_Material"
        self.SCRATCHES_MAT = self.__materials_path + "Procedural_Scratches_material/Scratches_Procedural"
        self.DIRT_MAT = self.__materials_path + "Procedural_Dirt_material/Dirt_Procedural_2"

        # Plate Dimensions: Single-line
        self.PLATE_TEX_WIDTH = 500
        self.PLATE_TEX_HEIGHT = 500

        # Plate Dimensions: 2-line
        self.PLATE_MULTILINE_TEX_WIDTH = 575
        self.PLATE_MULTILINE_TEX_WIDTH = 270

        # Call the other exts
        self.manip_suite = ManipulationSuite()
        self.looks_suite = LooksSuite()
        self.mov_suite = MovementSuite()
        self.cam_suite = CameraSuite()
        self.cap_suite = CaptureSuite()

        # Calling and setting up the WeatherSuite extension
        self.weatherController = WeatherSuite(
            path=Path(self.EXTENSION_FOLDER_PATH, "scene_utils/weather/").parent, lat=self.__lat, lon=self.__lon
        )

        self.WEATHER_OPTIONS = self.weatherController.get_available_effects()[1:]

        # Calling and setting up the PlateGenerator extension
        self.plate_generator = IndianLicensePlateGenerator(
            working_dir=self.EXTENSION_FOLDER_PATH,
            arm_bg_material=self.ARM_BG_MAT,
            arm_mil_bg_material=self.ARM_MIL_BG_MAT,
            regions_path=self.__rto_data_path,
            text_width=self.PLATE_TEX_WIDTH
        )

        #####################
        ## SCENE VARIABLES ##
        #####################

        # DataFrame for appending annotator
        self.gen_df = pd.DataFrame()

        # FONTS
        self.FONT_LIST = [str(i) for i in Path(self.EXTENSION_FOLDER_PATH, self.__font_path).rglob("*.ttf")]
        # Probability of white plate VS yellow plate
        self.PLATE_PROB = {"arm": 0.5, "arm_mil": 0.5}

        # Threshold for distance from camera before the LP is considered "unreadable" (based on the human eye)
        self.CAM_THRESH = 2500.0  # default: 1500.0

        # Currently selected vehicle
        self.CURR_VEHICLE = 0  # default: 0

        # Currently used font (if any)
        self.CURRENT_FONT = self.FONT_LIST[0]  # first font in the font list

        # The current weather effect active in the scene
        self.CURRENT_WEATHER = None  # default: None

        # Check if the current time of day is NIGHT!
        self.IS_NIGHT_TIME = False  # default: False

        # GET SCENE OBJECT PATHS HERE!
        # Refresh stage after loading
        self.STAGE = omni.usd.get_context().get_stage()

        # # CAMERAS
        # cams = self.STAGE.GetPrimAtPath(self.__cam_path)
        # self.CAMERAS = [str(p.GetPath()) for p in cams.GetChildren()]
        # self.CAMERA_NAMES = [i.split("/")[-1] for i in self.CAMERAS]

        # # LIGHTS
        # lights = self.STAGE.GetPrimAtPath(self.__lights_path)
        # self.LIGHTS = [str(p.GetPath()) for p in lights.GetChildren()]

        # # VEHICLES + LPS
        # vehs = self.STAGE.GetPrimAtPath(self.__vehicles_path)
        # self.VEHICLES = [str(p.GetChildren()[0].GetPath()) for p in vehs.GetChildren()]
        # self.VEHICLE_NAMES = [i.split("/")[-1] for i in self.VEHICLES]

        # # Create an empty string list to be assigned later
        # self.LICENSE_PLATES = [""] * len(self.VEHICLES)

        # # Set current vehicle as the selected one
        # self.SELECTION.set_selected_prim_paths([self.VEHICLES[self.CURR_VEHICLE]], True)

    #########################
    ## GETTERS AND SETTERS ##
    #########################

    # FPS SETTERS/GETTERS
    @property
    def fps(self) -> int:
        if self.__fps:
            return self.__fps

    @fps.setter
    def fps(self, value: int):
        self.__fps = value

    # CURRENT VEHICLE SETTERS/GETTERS
    @property
    def current_vehicle(self) -> int:
        return self.CURR_VEHICLE

    @current_vehicle.setter
    def current_vehicle(self, value: int):
        self.CURR_VEHICLE = value

    # RESOLUTION SETTERS/GETTERS
    @property
    def resolution(self) -> List:
        return self.__resolution

    @resolution.setter
    def resolution(self, value: List):
        self.__resolution = value

    @property
    def sdg_samples(self) -> int:
        return self.__sdg_samples

    @sdg_samples.setter
    def sdg_samples(self, value: int):
        self.__sdg_samples = value

    @property
    def latitude(self) -> float:
        return self.__lat

    @latitude.setter
    def latitude(self, value: float):
        self.__lat = value

    @property
    def longitude(self) -> float:
        return self.__lon

    @longitude.setter
    def longitude(self, value: float):
        self.__lon = value

    @property
    def bluriness(self) -> float:
        return self.__bluriness

    @bluriness.setter
    def bluriness(self, value: float):
        self.__bluriness = value

    @property
    def font_size(self) -> int:
        return self.__font_size

    @font_size.setter
    def font_size(self, value: int):
        self.__font_size = value

    @property
    def randomize_font(self) -> bool:
        return self.__randomize_font

    @randomize_font.setter
    def randomize_font(self, value: str):
        self.__randomize_font = value

    @property
    def save_dir(self) -> int:
        return self.__save_dir

    @save_dir.setter
    def save_dir(self, value: str):
        self.__save_dir = value

    #######################
    ## PRIVATE FUNCTIONS ##
    #######################

    async def initialize(self):
        # IMPORTANT!!!!!! PRE-LOAD THE SCENE TO BE ABLE TO SET VARIABLES!
        try:
            # _load_scene(self.__scene_dir)
            await self._load_scene_async(self.__scene_dir)
        except Exception as e:
            print(f"ERROR! Could not load stage; Traceback: {e}")

        # Kickstart everything! NOTE: USERS MUST WAIT HERE!
        asyncio.ensure_future(self._initialize_cars_with_lps())

    async def _load_scene_async(self, scene_dir):
        """Asynchronous stage loading"""

        scene_path = str(pathlib.Path(self.EXTENSION_FOLDER_PATH, scene_dir))

        # Load scene path from given usdc file
        result, error = await omni.usd.get_context().open_stage_async(
            scene_path, load_set=omni.usd.UsdContextInitialLoadSet.LOAD_NONE
        )

        self.STAGE = omni.usd.get_context().get_stage()

        if not result:
            print(error)
        else:
            print("LOADED: " + str(scene_path))

    def _load_scene(self, scene_dir):
        """Synchronous scene loading"""

        scene_path = str(pathlib.Path(self.EXTENSION_FOLDER_PATH, scene_dir))

        omni.usd.get_context().open_stage(scene_path, load_set=omni.usd.UsdContextInitialLoadSet.LOAD_NONE)

    async def _initialize_cars_with_lps(self):
        """Creates License Plates for all cars"""

        # GET SCENE OBJECT PATHS HERE!
        # Refresh stage after loading
        self.STAGE = omni.usd.get_context().get_stage()

        # CAMERAS
        cams = self.STAGE.GetPrimAtPath(self.__cam_path)
        self.CAMERAS = [str(p.GetPath()) for p in cams.GetChildren()]

        # LIGHTS
        lights = self.STAGE.GetPrimAtPath(self.__lights_path)
        self.LIGHTS = [str(p.GetPath()) for p in lights.GetChildren()]

        # VEHICLES + LPS
        vehs = self.STAGE.GetPrimAtPath(self.__vehicles_path)
        self.VEHICLES = [str(p.GetChildren()[0].GetPath()) for p in vehs.GetChildren()]

        # Create an empty string list to be assigned later
        self.LICENSE_PLATES = [""] * len(self.VEHICLES)

        # Set current vehicle as the selected one
        self.SELECTION.set_selected_prim_paths([self.VEHICLES[self.CURR_VEHICLE]], True)

        # Switch cam to default car
        self.cam_suite.switch_camera(self.VEHICLES[self.current_vehicle] + "/Follow_Camera")

        # Reset timeline
        self.mov_suite.set_point_on_timeline(0, fps=self.__fps)

        # Clear any previously stored data
        self.clear_data()

        # Generate LPs for all vehicles
        for current_vehicle in range(len(self.VEHICLES)):
            # If night: Switch all vehicle lights off
            self.manip_suite.toggle_visibility(
                self.STAGE, self.VEHICLES[current_vehicle] + "/Vehicle_Lights", is_visible=self.IS_NIGHT_TIME
            )

            # Assign LP to select vehicle
            lp = self.generate_lp("imagex", current_vehicle, randomize_font=self.randomize_font,
                                  current_font=self.CURRENT_FONT)

            self.LICENSE_PLATES[current_vehicle] = lp

    def _get_ground_truth(self, date, stage, vehicle, im_name, lp_text):
        veh_bbox, aligned_veh_bbox = self.manip_suite.calculate_bbox(stage, vehicle, return_raw=True)

        active_cam = self.cam_suite.get_current_cam()

        if self.cam_suite.is_in_cam_view(stage, active_cam, veh_bbox):
            # Calculates the 2D coordinates of the object with respect to the desired camera
            # veh_coords_2d = [
            #     self.cam_suite.point_to_pixel(
            #         stage,
            #         active_cam,
            #         aligned_veh_bbox.GetCorner(i),
            #         resolution=self.__resolution,
            #     )
            #     for i in range(8)
            # ]

            # Returns the 2D Bounding Box calculated from the 3D points
            # veh_bbox_2d = self.manip_suite.extract_bbox2D(veh_coords_2d)

            # print(f"Vehicle 2D Bounding Box: {veh_bbox_2d}")

            # self.append_annotator(
            #     ts=date,
            #     im_name=im_name,
            #     fps=self.__fps,
            #     lat=self.__lat,
            #     lon=self.__lon,
            #     frame=self.mov_suite.get_current_point_on_timeline(self.STAGE),
            #     obj_id=0,
            #     bbox2d=veh_bbox_2d,
            #     lp_text=lp_text,
            # )

            front_plate_path = vehicle + "/NumberPlateAsset_F/NumberPlate"
            back_plate_path = vehicle + "/NumberPlateAsset_R/NumberPlate"

            front_bbox, aligned_front_box = self.manip_suite.calculate_bbox(stage, front_plate_path, return_raw=True)

            back_bbox, aligned_back_box = self.manip_suite.calculate_bbox(stage, back_plate_path, return_raw=True)

            # Check if LP is viewable as front or back LP
            lp_bbox = None
            aligned_lp_bbox = None

            front_lp_dist = self.cam_suite.compute_distance_from_cam(stage, active_cam, aligned_front_box.GetCorner(0))
            back_lp_dist = self.cam_suite.compute_distance_from_cam(stage, active_cam, aligned_back_box.GetCorner(0))

            # Check distances of LPs w.r.t. camera
            # print(f"Front LP Dist: {front_lp_dist}, Back LP Dist: {back_lp_dist}")

            # Decide whether the current LP will be NONE, Front, or Back.
            if (front_lp_dist > 0) and (front_lp_dist <= self.CAM_THRESH) and (front_lp_dist < back_lp_dist):
                lp_bbox = front_bbox
                aligned_lp_bbox = aligned_front_box
                # print("Front plate detected")
            elif (back_lp_dist > 0) and (back_lp_dist <= self.CAM_THRESH) and (back_lp_dist < front_lp_dist):
                lp_bbox = back_bbox
                aligned_lp_bbox = aligned_back_box
                # print("Back plate detected")

            # Only bother with LPs if they're viewable in the frame :'D
            if lp_bbox is not None:
                bbox_in_view = [
                    self.cam_suite.is_in_cam_view(stage, active_cam, aligned_lp_bbox.GetCorner(i)) for i in range(8)
                ]

                # Now the LP has been detected, we need the LP text and shit
                if all(bbox_in_view):
                    # Calculates the 2D coordinates of the object with respect to the desired camera
                    lp_coords_2d = [
                        self.cam_suite.point_to_pixel(
                            stage,
                            active_cam,
                            aligned_lp_bbox.GetCorner(i),
                            resolution=self.__resolution,
                        )
                        for i in range(8)
                    ]

                    # Returns the 2D Bounding Box calculated from the 3D points
                    lp_bbox_2d = self.manip_suite.extract_bbox2D(lp_coords_2d)

                    # Show LP 2D Coordinates
                    # print(f"LP Coords: {lp_bbox_2d}")
                    lp_bbox_2d = list(lp_bbox_2d)
                    if "motorbike" in vehicle.lower():
                        y_go_up = 20
                        lp_bbox_2d[2] -= y_go_up
                        lp_bbox_2d[3] -= y_go_up
                    if "mercedes" in vehicle.lower():
                        y_go_up = 20
                        lp_bbox_2d[2] -= y_go_up
                        lp_bbox_2d[3] -= y_go_up
                    if "range" in vehicle.lower():
                        y_go_up = 10
                        lp_bbox_2d[2] -= y_go_up
                        lp_bbox_2d[3] -= y_go_up
                    self.append_annotator(
                        ts=date,
                        im_name=im_name,
                        fps=self.__fps,
                        lat=self.__lat,
                        lon=self.__lon,
                        frame=self.mov_suite.get_current_point_on_timeline(self.STAGE),
                        obj_id=1,
                        bbox2d=lp_bbox_2d,
                        lp_text=lp_text,
                    )

    ######################
    ## PUBLIC FUNCTIONS ##
    ######################

    async def generate_lp(self, im_name, current_vehicle, randomize_font=True, current_font=""):
        """Generates a License Plate for a select vehicle"""
        # Generate LP on current vehicle

        if randomize_font:
            current_font = self.FONT_LIST[np.random.choice(len(self.FONT_LIST))]
        else:
            current_font = current_font
        # current_font =

        vehicle_path = str(Path(self.EXTENSION_FOLDER_PATH, self.__plate_tex_path, str(current_vehicle) + "_"))

        lp_text = await asyncio.ensure_future(
            self.plate_generator.make_lp(
                self.STAGE,
                self.VEHICLES[current_vehicle],
                self.PLATE_TEX_WIDTH,
                self.PLATE_TEX_HEIGHT,
                vehicle_path,
                self.PLATE_PROB,
                current_font,
                im_name,
                bluriness=self.bluriness,
                sobel=0,
                padding=12,
                linespace=0,
                multiline=False,
                show_lp_text=True,
            )
        )
        return lp_text

    def get_directory_size(self, directory):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        size_in_mb = total_size / (1024 * 1024)
        return size_in_mb

    def clear_cache(self, directory):
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                if "plate" in f and "image" in f:
                    fp = os.path.join(dirpath, f)
                    os.remove(fp)

    async def randomize_scene(self, im_name="-1", rendermode="PathTracing", save=False):
        # Clear data so that the randomizer can append new data
        self.clear_data()
        directory_path = '/home/guest/.cache/ov'
        size_in_mb = self.get_directory_size(directory_path)
        if size_in_mb > 20000:
            self.clear_cache(directory_path)

        # 1) Position Cars
        timeline_pos = np.random.randint(0, self.mov_suite.get_end_timecode(self.STAGE))
        self.mov_suite.set_point_on_timeline(timeline_pos, fps=self.__fps)
        now_time = pd.to_datetime("today")

        # 1) Select Camera
        camera_sel = np.random.randint(0, len(self.CAMERAS))
        self.cam_suite.switch_camera(self.CAMERAS[camera_sel])

        # 2) Set Time-Of-Day (based on capture time)
        tod_hour = now_time.hour
        self.weatherController.configure_time_of_day(tod_hour)

        # 3) Control Lights (hour-based)
        show_lights = True if (tod_hour >= 21 and tod_hour <= 6) else False
        self.IS_NIGHT_TIME = show_lights

        [self.manip_suite.toggle_visibility(self.STAGE, light, is_visible=show_lights) for light in self.LIGHTS]

        # Just wait until the cam has switched a little
        await asyncio.sleep(1)

        # 4) Generate LPs for all vehicles
        for current_vehicle in range(len(self.VEHICLES)):

            # Assign LP to select vehicle
            lp = await asyncio.ensure_future(
                self.generate_lp(im_name, current_vehicle, current_font=self.CURRENT_FONT,
                                 randomize_font=self.randomize_font))

            self.manip_suite.toggle_visibility(
                self.STAGE, self.VEHICLES[current_vehicle] + "/Vehicle_Lights", is_visible=show_lights
            )

            self.LICENSE_PLATES[current_vehicle] = lp

            # Annotate!
            if save:
                self._get_ground_truth(
                    now_time.strftime(self.__strf_datetime),
                    self.STAGE,
                    self.VEHICLES[current_vehicle],
                    im_name,
                    self.LICENSE_PLATES[current_vehicle],
                )

        # Capture delay
        await asyncio.sleep(1)

        if save:
            # Save LPs in dedicated path
            self.save_annotations(now_time.strftime(self.__strf_date), annotations_path=self.DATA_PATH)

            # Clear data so we don't keep old annotations
            self.clear_data()

            # Take respective screenshot :D
            await self.cap_suite.take_screenshot_async(
                f"{self.IM_PATH}/{im_name}",
                use_custom_camera=False,
                resolution=self.__resolution,
                rendermode=rendermode,
                spp=self.__spp,
            )

    async def create_synthetic_data(self, synthetic_samples, rendermode="PathTracing"):
        for i in tqdm(range(synthetic_samples), desc=f"Generating Plates", file=sys.stdout):
            await asyncio.ensure_future(
                self.randomize_scene(im_name=(str(i).zfill(8) + ".png"), rendermode=rendermode, save=True)
            )

    def append_annotator(self, ts, im_name, fps, frame, obj_id, bbox2d, lp_text, lat, lon):
        """Appends LP information to the designated .csv file"""
        new_row = pd.DataFrame(
            [{
                "TS": ts,
                "Image": im_name,
                "FPS": fps,
                "Frame_No": frame,
                "Latitude": lat,
                "Longitude": lon,
                "Object_ID": obj_id,
                "x1": bbox2d[0],
                "y1": bbox2d[2],
                "x2": bbox2d[1],
                "y2": bbox2d[3],
                "LP_Text": lp_text,
            }]
        )
        self.gen_df = pd.concat([self.gen_df, new_row], ignore_index=True)

    def save_annotations(self, date, annotations_path):
        """Saves the LP information to a selected annotation path"""
        # Create annotations path if it does not exist
        if not os.path.exists(annotations_path):
            os.mkdir(annotations_path)

        # If .csv for that day exists, append to it, else create a new file
        if os.path.exists(f"{annotations_path}/synth_veh_data_{str(date)}.csv"):
            self.gen_df.to_csv(
                f"{annotations_path}/synth_veh_data_{str(date)}.csv", header=False, index=False, mode="a+"
            )
        else:
            self.gen_df.to_csv(f"{annotations_path}/synth_veh_data_{str(date)}.csv", index=False)

    def clear_data(self):
        """Clears accumulated data"""
        self.gen_df = pd.DataFrame()

    ##################
    ## UI FUNCTIONS ##
    ##################

    def adjust_motion_blur(self, model):
        self.settings.set("/rtx/post/motionblur/maxBlurDiameterFraction", (model.get_value_as_float() / 100.0))

    def adjust_fog(self, model):
        self.settings.set("/rtx/fog/fogColorIntensity", (model.get_value_as_float() / 100.0))

    def set_sdg_samples(self, model):
        self.sdg_samples = model.get_value_as_int()

    def set_latitude(self, model):
        self.latitude = model.get_value_as_float()
        self.weatherController.configure_lat(self.latitude)

    def set_longitude(self, model):
        self.longitude = model.get_value_as_float()
        self.weatherController.configure_lon(self.longitude)

    def set_resolution_x(self, model):
        self.resolution = [model.get_value_as_int(), self.resolution[1]]
        self.cam_suite.set_resolution(self.resolution)

    def set_resolution_y(self, model):
        self.resolution = [self.resolution[0], model.get_value_as_int()]
        self.cam_suite.set_resolution(self.resolution)

    def set_normalmap(self, model):
        """Adjust normal map generation intensity AS AN ODD NUMBER!"""
        self.bluriness = (model.get_value_as_int() * 2) + 1

    def set_font_size(self, model):
        """Adjust font size"""
        self.font_size = model.get_value_as_int()

    def set_scratch_intensity_front(self, model):
        mat_path = (
                self.VEHICLES[
                    self.current_vehicle] + "/Shared_Materials/Procedural_Scratches_material/Scratches_Procedural"
        )
        object_path = self.VEHICLES[self.current_vehicle] + "/NumberPlateAsset_F/Damage_Scratches"
        param_name = "opacity_threshold"
        param_value = 1 - (model.get_value_as_float() / 100)

        self.looks_suite.modify_float_parameter(self.STAGE, object_path, mat_path, param_name, param_value)

    def set_scratch_intensity_rear(self, model):
        mat_path = (
                self.VEHICLES[self.current_vehicle]
                + "/Shared_Materials/Procedural_Scratches_material_01/Scratches_Procedural"
        )
        object_path = self.VEHICLES[self.current_vehicle] + "/NumberPlateAsset_R/Damage_Scratches"
        param_name = "opacity_threshold"
        param_value = 1 - (model.get_value_as_float() / 100)

        self.looks_suite.modify_float_parameter(self.STAGE, object_path, mat_path, param_name, param_value)

    def set_dirt_intensity_front(self, model):
        mat_path = self.VEHICLES[self.current_vehicle] + "/Shared_Materials/Procedural_Dirt_material/Dirt_Procedural_2"
        object_path = self.VEHICLES[self.current_vehicle] + "/NumberPlateAsset_F/Damage_Dirt"
        param_name = "opacity_threshold"
        param_value = 1 - (model.get_value_as_float() / 100)

        self.looks_suite.modify_float_parameter(self.STAGE, object_path, mat_path, param_name, param_value)

    def set_dirt_intensity_rear(self, model):
        mat_path = (
                self.VEHICLES[self.current_vehicle] + "/Shared_Materials/Procedural_Dirt_material_01/Dirt_Procedural_2"
        )
        object_path = self.VEHICLES[self.current_vehicle] + "/NumberPlateAsset_R/Damage_Dirt"
        param_name = "opacity_threshold"
        param_value = 1 - (model.get_value_as_float() / 100)

        self.looks_suite.modify_float_parameter(self.STAGE, object_path, mat_path, param_name, param_value)

    def toggle_bounding_boxes(self, model):
        """Toggle if bounding boxes are on or off!"""
        show_bbox = model.get_value_as_bool()

        if show_bbox == True:
            for vehicle in self.VEHICLES:
                self.manip_suite.toggle_visibility(self.STAGE, vehicle + "/BoundingBox", is_visible=show_bbox)

        else:
            for vehicle in self.VEHICLES:
                self.manip_suite.toggle_visibility(self.STAGE, vehicle + "/BoundingBox", is_visible=show_bbox)

    def toggle_scene_lights(self, model):
        show_lights = model.get_value_as_bool()
        [self.manip_suite.toggle_visibility(self.STAGE, light, is_visible=show_lights) for light in self.LIGHTS]

    def toggle_vehicle_lights(self, model):
        toggle_light = model.get_value_as_bool()
        self.manip_suite.toggle_visibility(
            self.STAGE, self.VEHICLES[self.current_vehicle] + "/Vehicle_Lights", is_visible=toggle_light
        )

    def toggle_resolution(self, model):
        self.__rendermode = "PathTracing" if model.get_value_as_int() == 1 else "RayTracedLighting"

    def set_weather(self, model):
        """Create (or destroy) active weather effects"""
        weather_pos = self.cam_suite.get_position(self.STAGE, self.cam_suite.get_current_cam())

        # Spawn the respective weather effect
        self.weatherController.configure_weather(
            stage=self.STAGE,
            prefix="/Root/Weather_Effect",
            position=(weather_pos[0], weather_pos[1], weather_pos[2]),
            weather_desc=self.WEATHER_OPTIONS[model.get_item_value_model().as_int],
        )

    def set_lp_bg(self, model):
        """Set License Plate to exclusively WHITE or YELLOW"""
        if model.get_item_value_model().get_value_as_int() == 0:
            self.PLATE_PROB = {"private": 1.0, "commercial": 0.0}
        else:
            self.PLATE_PROB = {"private": 0.0, "commercial": 1.0}

    def set_font_type(self, model):
        self.CURRENT_FONT = self.FONT_LIST[model.get_item_value_model().get_value_as_int()]
        self.randomize_font = False

    def set_fps_value(self, model):
        self.fps = model.get_item_value_model().get_value_as_int()

    def set_active_camera(self, model):
        self.cam_suite.switch_camera(self.CAMERAS[model.get_item_value_model().get_value_as_int()])

    def set_active_vehicle(self, model):
        curr_vehicle = model.get_item_value_model().get_value_as_int()

        # Fixes a weird bug where the dropdown at '0' is not set to this (???)
        self.current_vehicle = curr_vehicle

        # Switch camera and create selection
        self.cam_suite.switch_camera(self.VEHICLES[curr_vehicle] + f"/Follow_Camera")
        self.SELECTION.set_selected_prim_paths([self.VEHICLES[curr_vehicle]], True)

    def generate_lp_on_current_vehicle(self):
        self.generate_lp(
            current_vehicle=self.current_vehicle, randomize_font=self.randomize_font, current_font=self.CURRENT_FONT
        )

    def generate_synthetic_data(self):
        asyncio.ensure_future(
            self.create_synthetic_data(synthetic_samples=self.__sdg_samples, rendermode=self.__rendermode)
        )

    async def capture_scene(self):
        now_time = pd.to_datetime("today")

        im_name = now_time.strftime(STRF_DATE) + ".png"

        single_capture_path = "single_capture"

        for current_vehicle in range(len(self.VEHICLES)):
            # ANNOTATE!!!
            self._get_ground_truth(
                now_time.strftime(STRF_DATETIME),
                self.STAGE,
                self.VEHICLES[current_vehicle],
                im_name,
                self.LICENSE_PLATES[current_vehicle],
            )

        # Save LPs in dedicated path
        self.save_annotations(
            now_time.strftime(self.__strf_date), annotations_path=pathlib.Path(self.DATA_PATH, single_capture_path)
        )

        # Clear data so we don't keep old annotations
        self.clear_data()

        # Capture delay
        await asyncio.sleep(1)

        # Take respective screenshot :D
        await self.cap_suite.take_screenshot_async(
            f"{self.IM_PATH}/{single_capture_path}/{im_name}",
            use_custom_camera=False,
            resolution=RESOLUTION,
            rendermode="PathTracing",
            spp=SPP,
        )
