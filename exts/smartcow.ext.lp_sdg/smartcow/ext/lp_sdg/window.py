import omni.ui as ui

from typing import Callable, List

import carb
import os
import asyncio

# Style and functions
from .style import STYLE, ATTR_LABEL_WIDTH
from .lp_sdg_control_panel import LP_SDG_Control_Panel

# Custom functions import
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_slider_widget import CustomSliderWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_field_widget import CustomFieldWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_toggle_widget import CustomToggleWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_bool_widget import CustomBoolWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_color_widget import CustomColorWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_combobox_widget import CustomComboboxWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_multifield_widget import CustomMultifieldWidget
from smartcow.ext.lp_sdg.custom_widgets.lpsdg_filepicker_widget import CustomFilePickerWidget

# UI Spacing
SPACING = 5


class LPSDGWindow(ui.Window):
    """A class that represents the entire UI Window for LP-SDG"""

    def __init__(self, title: str, delegate=None, **kwargs):
        self.__label_width = ATTR_LABEL_WIDTH

        super().__init__(title, **kwargs)

        # Apply the style to all the widgets of this window
        self.frame.style = STYLE

        # Build function override
        self.frame.set_build_fn(self._build_fn)

    def destroy(self):
        # Destroys all the children
        super().destroy()

    @property
    def label_width(self):
        """The width of the attribute label"""
        return self.__label_width

    @label_width.setter
    def label_width(self, value):
        """The width of the attribute label"""
        self.__label_width = value
        self.frame.rebuild()

    def re_initialize(self):
        asyncio.ensure_future(self.lp_sdg_control_panel.initialize())

    def _build_collapsable_header(self, collapsed, title):
        """Build a custom title of CollapsableFrame"""
        with ui.VStack():
            ui.Spacer(height=8)

            with ui.HStack(height=0):
                ui.Spacer(width=SPACING * 2)
                # Collapsed image before Collapsable Header Title
                if collapsed:
                    image_name = "collapsed_opened"
                else:
                    image_name = "collapsed_closed"
                ui.Image(name=image_name, width=10, height=10)
                ui.Spacer(width=SPACING * 2)

                ui.Label(title, name="collapsable_name")

            ui.Spacer(height=8)

    def _build_scene(self):
        """Build the widgets of the "Scene Settings" group"""
        with ui.CollapsableFrame(
            "Scene Settings".upper(), name="group", build_header_fn=self._build_collapsable_header
        ):
            with ui.VStack(height=0, spacing=SPACING * 2):
                # Motion Blur Widget
                motion_blur_widget = CustomSliderWidget(
                    min=0, max=100, num_type="int", default_val=35.0, label="Motion Blur Intensity"
                )
                motion_blur_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.adjust_motion_blur(m))

                # Synthetic Samples Widget; Sample #
                sdg_samples_widget = CustomFieldWidget(
                    num_type="int",
                    default_val=self.lp_sdg_control_panel.sdg_samples,
                    min=0,
                    max=10000,
                    label="No. of Synthetic Samples",
                )
                sdg_samples_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.set_sdg_samples(m))

                # Scene Lights Button
                scene_lights_widget = CustomToggleWidget(
                    first_option="On", second_option="Off", default_val=True, label="Show Scene Lights"
                )
                scene_lights_widget.model.add_value_changed_fn(
                    lambda m: self.lp_sdg_control_panel.toggle_scene_lights(m)
                )

                # Bounding Box toggle on/off
                bbox_widget = CustomToggleWidget(
                    first_option="On", second_option="Off", default_val=False, label="Show Bounding Boxes"
                )
                bbox_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.toggle_bounding_boxes(m))

                # Creates empty space so that UI can have right-orientation!
                with ui.HStack(height=0):
                    ui.Button(
                        "Initialize Scene",
                        clicked_fn=lambda: self.re_initialize()
                    )
                    ui.Button(
                        "Randomise Scene",
                        clicked_fn=lambda: asyncio.ensure_future(self.lp_sdg_control_panel.randomize_scene()),
                    )
                    ui.Spacer(width=SPACING)
                    ui.Button(
                        "Capture Scene",
                        clicked_fn=lambda: asyncio.ensure_future(self.lp_sdg_control_panel.capture_scene()),
                    )
                    ui.Spacer(width=SPACING)

                ui.Spacer()

    def _build_cameras(self):
        """Build the widgets of the "Camera Settings" group"""
        with ui.CollapsableFrame(
            "Camera Settings".upper(), name="group", build_header_fn=self._build_collapsable_header, collapsed=True
        ):
            with ui.VStack(height=0, spacing=SPACING * 2):
                # Camera List
                camera_widget = CustomComboboxWidget(
                    options=self.lp_sdg_control_panel.CAMERA_NAMES,
                    default_value=0,
                    label="Selected Camera",
                )

                camera_widget.model.add_item_changed_fn(lambda m, _: self.lp_sdg_control_panel.set_active_camera(m))

                # Resolution slider
                resolution_widget = CustomMultifieldWidget(
                    sublabels=["W: ", "H: "],
                    default_vals=self.lp_sdg_control_panel.resolution,
                    num_type="int",
                    label="Resolution",
                )

                resolution_widget.multifields[0].model.add_value_changed_fn(
                    lambda m: self.lp_sdg_control_panel.set_resolution_x(m)
                )

                resolution_widget.multifields[1].model.add_value_changed_fn(
                    lambda m: self.lp_sdg_control_panel.set_resolution_y(m)
                )

                ui.Spacer()

    def _build_vehicles(self):
        """Build the widgets of the "Vehicle Settings" group"""
        with ui.CollapsableFrame(
            "Vehicle Settings".upper(), name="group", build_header_fn=self._build_collapsable_header, collapsed=True
        ):
            with ui.VStack(height=0, spacing=SPACING * 2):
                # Vehicle List
                vehicles_widget = CustomComboboxWidget(
                    options=self.lp_sdg_control_panel.VEHICLE_NAMES,
                    default_value=0,
                    label="Selected Vehicle",
                )
                vehicles_widget.model.add_item_changed_fn(lambda m, _: self.lp_sdg_control_panel.set_active_vehicle(m))

                ui.Spacer()

                # License Plate Settings for individual vehicles
                with ui.ZStack(height=300):
                    ui.Rectangle(name="SubWindow")

                    ui.Spacer(height=SPACING)

                    with ui.VStack(spacing=SPACING):
                        ui.Label("")

                        # Vehicle Lights ON/OFF Options
                        vehicle_lights_widget = CustomToggleWidget(
                            first_option="On", second_option="Off", default_val=False, label="Vehicle Lights"
                        )
                        vehicle_lights_widget.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.toggle_vehicle_lights(m)
                        )

                        ui.Line(style_type_name_override="HeaderLine")

                        # FONTS Combobox widget
                        font_select_widget = CustomComboboxWidget(
                            options=[os.path.basename(i.split("/")[-1]) for i in self.lp_sdg_control_panel.FONT_LIST],
                            default_value=0,
                            label="License Plate Font",
                        )

                        font_select_widget.model.add_item_changed_fn(
                            lambda m, _: self.lp_sdg_control_panel.set_font_type(m)
                        )

                        # Normal Map intensity widget
                        normalmap_widget = CustomSliderWidget(
                            min=0,
                            max=5,
                            num_type="int",
                            default_val=0,
                            label="License Plate Font Blurring Intensity",
                        )
                        normalmap_widget.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.set_normalmap(m)
                        )

                        # Scratch Intensity Widget
                        scratch_widget_front = CustomSliderWidget(
                            min=0, max=100, num_type="int", default_val=35.0, label="Scratch Intensity (F)"
                        )
                        scratch_widget_front.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.set_scratch_intensity_front(m)
                        )

                        scratch_widget_back = CustomSliderWidget(
                            min=0, max=100, num_type="int", default_val=35.0, label="Scratch Intensity (R)"
                        )
                        scratch_widget_back.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.set_scratch_intensity_rear(m)
                        )

                        # Dirt Intensity Widget
                        dirt_widget_front = CustomSliderWidget(
                            min=0, max=100, num_type="int", default_val=0.0, label="Dirt Intensity (F)"
                        )
                        dirt_widget_front.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.set_dirt_intensity_front(m)
                        )

                        # Dirt Intensity Widget
                        dirt_widget_back = CustomSliderWidget(
                            min=0, max=100, num_type="int", default_val=0.0, label="Dirt Intensity (R)"
                        )
                        dirt_widget_back.model.add_value_changed_fn(
                            lambda m: self.lp_sdg_control_panel.set_dirt_intensity_rear(m)
                        )

                        ui.Label("")

                    ui.Spacer(height=SPACING)

                ui.Spacer()

                # Creates empty space so that UI can have right-orientation!
                with ui.HStack(height=0):
                    with ui.HStack(width=ui.Percent(30)):
                        ui.Spacer(width=SPACING // 2)
                        ui.Label("")

                    self._top_container = ui.Stack(ui.Direction.LEFT_TO_RIGHT)
                    with self._top_container:
                        with ui.HStack():
                            ui.Button(
                                "Generate License Plate",
                                clicked_fn=lambda: self.lp_sdg_control_panel.generate_lp_on_current_vehicle(),
                            )
                            ui.Spacer(width=SPACING)

                ui.Spacer()

    def _build_environment(self):
        """Build the widgets of the "Environment Settings" group"""
        with ui.CollapsableFrame(
            "Environment Settings".upper(), name="group", build_header_fn=self._build_collapsable_header, collapsed=True
        ):
            with ui.VStack(height=0, spacing=SPACING * 2):
                # Lat & Lon
                lat_widget = CustomFieldWidget(
                    num_type="float",
                    default_val=self.lp_sdg_control_panel.latitude,
                    min=-85.05115,
                    max=85.05115,
                    label="Latitude",
                )
                lat_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.set_latitude(m))

                lon_widget = CustomFieldWidget(
                    num_type="float",
                    default_val=self.lp_sdg_control_panel.longitude,
                    min=-180,
                    max=180,
                    label="Longitude",
                )
                lon_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.set_longitude(m))

                # Weather Effect
                weather_widget = CustomComboboxWidget(
                    options=["Sun", "Rain", "Snow"], default_value=0, label="Weather Effect Selection"
                )
                weather_widget.model.add_item_changed_fn(lambda m, _: self.lp_sdg_control_panel.set_weather(m))

                # Fog Intensity
                fog_widget = CustomSliderWidget(min=0, max=100, num_type="int", default_val=25.0, label="Fog Intensity")
                fog_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.adjust_fog(m))

                ui.Spacer()

    def _build_capture(self):
        """Build the widgets of the "Capture Settings" group"""
        with ui.CollapsableFrame(
            "Capture Settings".upper(), name="group", build_header_fn=self._build_collapsable_header, collapsed=True
        ):
            with ui.VStack(height=0, spacing=SPACING * 2):
                # Resolution slider
                resolution_widget = CustomMultifieldWidget(
                    sublabels=["W: ", "H: "],
                    default_vals=self.lp_sdg_control_panel.resolution,
                    num_type="int",
                    label="Resolution",
                )

                resolution_widget.multifields[0].model.add_value_changed_fn(
                    lambda m: self.lp_sdg_control_panel.set_resolution_x(m)
                )

                resolution_widget.multifields[1].model.add_value_changed_fn(
                    lambda m: self.lp_sdg_control_panel.set_resolution_y(m)
                )

                # Toggle RenderMode Type
                render_widget = CustomToggleWidget(
                    first_option="RTX Real-Time", second_option="Path-Tracing", label="Render Mode"
                )
                render_widget.model.add_value_changed_fn(lambda m: self.lp_sdg_control_panel.toggle_resolution(m))

                # FilePicker to select custom save path
                CustomFilePickerWidget(label="Save Directory", filepath=self.lp_sdg_control_panel.save_dir)

                # Creates empty space so that UI can have right-orientation!
                with ui.HStack(height=0):
                    with ui.HStack(width=ui.Percent(30)):
                        ui.Spacer(width=SPACING // 2)
                        ui.Label("")

                    self._top_container = ui.Stack(ui.Direction.LEFT_TO_RIGHT)
                    with self._top_container:
                        with ui.HStack():
                            ui.Button(
                                "Generate Synthetic Samples",
                                clicked_fn=lambda: self.lp_sdg_control_panel.generate_synthetic_data(),
                            )
                            ui.Spacer(width=SPACING)

                ui.Spacer()

    def _build_fn(self):
        """
        This is the method called to build the UI once the window is instantiated
        """

        # Get the LP SDG Backend Functionality
        self.lp_sdg_control_panel = LP_SDG_Control_Panel()

        # Put it all together!
        with ui.ScrollingFrame(name="window_bg", horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF):
            with ui.VStack(height=0):
                self._build_scene()
                self._build_cameras()
                self._build_vehicles()
                self._build_environment()
                self._build_capture()
