from omni import ui

import omni.kit.app

from omni.ui import color as cl
from omni.ui import constant as fl
from omni.ui import url

import pathlib

# Path to ROOT extension
EXTENSION_FOLDER_PATH = pathlib.Path(
    omni.kit.app.get_app().get_extension_manager().get_extension_path_by_module(__name__)
)

ATTR_LABEL_WIDTH = 150
BLOCK_HEIGHT = 22
TAIL_WIDTH = 35

# Revert Icon Variables
REVERT_ICON_WIDTH = 15
REVERT_ICON_HEIGHT = 20

# Window Variables
WIN_WIDTH = 500
WIN_HEIGHT = 500

######################
## COLOUR CONSTANTS ##
######################

# Main window
cl.window_bg_color = cl(0.2, 0.2, 0.2, 0.5)
cl.window_title_text = cl(0.9, 0.9, 0.9, 1.0)

# Subwindows (darker spaces)
cl.subwindow_bg_color = cl(0.13, 0.13, 0.13, 1.0)

# Collapsible frame variables
cl.collapsible_header_text = cl(0.05, 0.05, 0.05, 1.0)
cl.collapsible_header_background = cl(0.16, 0.16, 0.16, 1.0)

# Label colour definitions
cl.main_attr_label_text = cl(0.76, 0.77, 0.80, 1.0)
cl.multifield_label_text = cl(0.65, 0.65, 0.65, 1.0)

# Combobox colour definitions
cl.combobox_label_text = cl(0.65, 0.65, 0.65, 1.0)

# Field AND/OR Slider Colours
cl.field_slider_bg = cl(0.08, 0.08, 0.08, 1.0)
cl.field_slider_secondary_col = cl(0.67, 0.67, 0.67, 1.0)
cl.field_slider_hover = cl(0.1, 0.1, 0.1, 1.0)
cl.slider_text = cl(0.87, 0.87, 0.87, 1.0)

# Toggles
cl.toggle_on = cl(0.05, 0.05, 0.05, 1.0)
cl.toggle_off = cl(0.11, 0.11, 0.11, 1.0)
cl.toggle_text_on = cl(0.76, 0.77, 0.80, 1.0)
cl.toggle_text_off = cl(0.5, 0.5, 0.5, 1.0)

# "Reset" arrow
cl.revert_arrow_enabled = cl(0.25, 0.5, 0.75, 1.0)
cl.revert_arrow_disabled = cl(0.35, 0.35, 0.35, 1.0)

# Misc. Colour definitions
cl.transparent = cl(0.0, 0.0, 0.0, 0.0)
cl.standard_text = cl(1.0, 1.0, 1.0, 1.0)
cl.smartcow_yellow = cl(1.00, 0.76, 0.0, 1.0)

#####################
## FLOAT CONSTANTS ##
#####################

# Variable constants
fl.main_label_attr_hspacing = 10
fl.attr_label_v_spacing = 3
fl.collapsable_group_spacing = 2
fl.outer_frame_padding = 5
fl.tail_icon_width = 15
fl.border_radius = 5
fl.button_border_radius = 10
fl.margin = 10
fl.margin_subwindow = 5
fl.padding = 5
fl.window_title_font_size = 24
fl.field_text_font_size = 14
fl.main_label_font_size = 14
fl.multi_attr_label_font_size = 14
fl.radio_group_font_size = 14
fl.collapsable_header_font_size = 18
fl.range_text_size = 10

#####################
## IMAGE CONSTANTS ##
#####################

# Misc Icons to help build UI
url.closed_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/collapsed_closed.svg"
url.open_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/collapsed_opened.svg"
url.select_dir = f"{EXTENSION_FOLDER_PATH}/icons/choose_filepath.svg"
url.open_curr_dir = f"{EXTENSION_FOLDER_PATH}/icons/open_curr_filepath.svg"
url.revert_arrow_icon = f"{EXTENSION_FOLDER_PATH}/icons/revert_arrow.svg"
url.checkbox_on_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_on.svg"
url.checkbox_off_icon = f"{EXTENSION_FOLDER_PATH}/icons/checkbox_off.svg"
url.radio_btn_on_icon = f"{EXTENSION_FOLDER_PATH}/icons/radio_btn_on.svg"
url.radio_btn_off_icon = f"{EXTENSION_FOLDER_PATH}/icons/radio_btn_off.svg"

# The style definition
STYLE = {
    "Rectangle::SubWindow": {
        "background_color": cl.subwindow_bg_color,
        "border_radius": fl.border_radius,
        "margin_width": fl.margin_subwindow,
    },
    "Rectangle::Toggle_ON_L":{
        "background_color": cl.toggle_on,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.LEFT,
    },
    "Rectangle::Toggle_ON_R":{
        "background_color": cl.toggle_on,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.RIGHT,
    },
    "Rectangle::Toggle_OFF_L":{
        "background_color": cl.toggle_off,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.LEFT,
    },
    "Rectangle::Toggle_OFF_R":{
        "background_color": cl.toggle_off,
        "border_radius": fl.border_radius,
        "corner_flag": ui.CornerFlag.RIGHT,
    },
    "Label::Toggle_ON": {"color": cl.toggle_text_on},
    "Label::Toggle_OFF": {"color": cl.toggle_text_off},
    "Label::attribute_name": {
        "margin_height": fl.attr_label_v_spacing,
        "margin_width": fl.main_label_attr_hspacing,
        "font_size": fl.main_label_font_size,
        "color": cl.main_attr_label_text,
    },
    "Label::attribute_name:hovered": {"color": cl.main_attr_label_text},
    "Label::field_tail": {
        "margin_height": fl.attr_label_v_spacing,
        "margin_width": fl.main_label_attr_hspacing,
        "color": cl.main_attr_label_text,
        "font_size": fl.main_label_font_size,
        "color": cl.main_attr_label_text,
    },
    "Field::stringfield": {
        "background_color": cl.field_slider_bg,
        "border_radius": fl.border_radius,
        "font_size": fl.field_text_font_size,
        "color": cl.slider_text,
        "padding": 4,
    },
    "Field::stringfield:hovered": {
        "background_color": cl.field_slider_hover,
    },
    "Field::intdrag": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_bg,
        "font_size": fl.field_text_font_size,
        "color": cl.slider_text,
    },
    "Field::intdrag:hovered": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_hover,
        "font_size": fl.field_text_font_size,
        "color": cl.slider_text,
    },
    "Field::multifield_attr": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_bg,
        "font_size": fl.field_text_font_size,
        "color": cl.standard_text,
    },
    "Field::multifield_attr:hovered": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_hover,
        "font_size": fl.field_text_font_size,
        "color": cl.standard_text,
    },
    "Field::path_field": {
        "font_size": fl.field_text_font_size,
    },
    "Slider::customslider": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_bg,
        "secondary_color": cl.field_slider_secondary_col,
        "color": cl.slider_text,
    },
    "Slider::customslider:hovered": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_hover,
        "secondary_color": cl.field_slider_secondary_col,
        "color": cl.slider_text,
    },
    "Slider::intdrag": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_bg,
        "secondary_color": cl.transparent,
        "font_size": fl.field_text_font_size,
        "color": cl.slider_text,
    },
    "Slider::intdrag:hovered": {
        "border_radius": fl.border_radius,
        "background_color": cl.field_slider_hover,
        "font_size": fl.field_text_font_size,
        "color": cl.slider_text,
    },
    "Button": {
        "background_color": cl.smartcow_yellow,
        "border_radius": fl.button_border_radius,
        "padding": fl.padding,
    },
    "Button.Label": {
        "color": cl(0.2, 0.2, 0.2, 1.0),
    },
    "Button:hovered": {"background_color": 0xFF4DD5FF},
    "Button:pressed": {"background_color": 0xFF0990F7},
    "ComboBox": {"border_radius": fl.border_radius},
    "CollapsableFrame::group": {
        "margin_height": fl.collapsable_group_spacing,
        "background_color": cl.collapsible_header_background,
        "secondary_color": cl.collapsible_header_background,
        "border_radius": 5,
        "margin": fl.margin,
        "padding": fl.padding,
    },
    "CollapsableFrame::group:hovered": {
        "background_color": cl.collapsible_header_background,
    },
    "Image::collapsed_opened": {
        "image_url": url.open_arrow_icon,
    },
    "Image::collapsed_opened:hovered": {
        "image_url": url.open_arrow_icon,
    },
    "Image::collapsed_closed": {
        "image_url": url.closed_arrow_icon,
    },
    "Image::collapsed_closed:hovered": {
        "image_url": url.closed_arrow_icon,
    },
    "Image::checked": {"image_url": url.checkbox_on_icon},
    "Image::unchecked": {"image_url": url.checkbox_off_icon},
    "Image::revert_arrow": {
        "image_url": url.revert_arrow_icon,
        "color": cl.revert_arrow_enabled,
    },
    "Image::revert_arrow:disabled": {"color": cl.revert_arrow_disabled},
    "Image::select_dir": {"image_url": url.select_dir},
    "Image::open_curr_dir": {"image_url": url.open_curr_dir},
    "ColorWidget": {
        "border_radius": fl.border_radius,
        "border_color": cl(0.0, 0.0, 0.0, 0.0),
        "background_color": cl.field_slider_bg,
    },
    "ComboBox::dropdown_menu": {
        "color": cl.slider_text,  # label color
        "padding_height": 4,
        "margin": 5,
        "background_color": cl.field_slider_bg,
        "border_radius": fl.border_radius,
        "font_size": fl.field_text_font_size,
        "secondary_color": cl.field_slider_secondary_col,  # button background color
    },
    "CheckBox::invisible_checkbox":{
        "color": cl.transparent,
        "background_color": cl.transparent,
    },
    "ScrollingFrame::window_bg": {
        "background_color": cl.window_bg_color,
        "padding": fl.outer_frame_padding,
        "border_radius": 10,  # Not obvious in a window, but more visible with only a frame
    },
    "HeaderLine": {
        "color": cl(0.5, 0.5, 0.5, 0.5),
        "margin_width": fl.margin_subwindow,
    },
}
