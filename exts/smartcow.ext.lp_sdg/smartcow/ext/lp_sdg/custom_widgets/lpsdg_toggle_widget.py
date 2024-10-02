from ctypes import alignment
from typing import Optional

import omni.ui as ui

from .lpsdg_base_widget import CustomBaseWidget

TOGGLE_BUTTON_WIDTH_PERCENT = 50

class CustomToggleWidget(CustomBaseWidget):
    """
    A widget for toggle input.
    """

    def __init__(
        self, model: ui.AbstractItemModel = None, default_val: bool = True, first_option="", second_option="", **kwargs
    ):
        self.__default_val = default_val
        self.__first_option = first_option
        self.__second_option = second_option

        self.__first_opt = None
        self.__first_opt_rect = None
        self.__second_opt = None
        self.__second_opt_rect = None

        self.__selection_model = ui.SimpleBoolModel(default_val)
        
        self.__checkbox = None

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__first_opt = None
        self.__first_opt_rect = None
        self.__second_opt = None
        self.__second_opt_rect = None
        self.__selection_model = None

    @property
    def model(self) -> Optional[ui.AbstractValueModel]:
        """The widget's model"""
        if self.__checkbox.model:
            return self.__checkbox.model

    @model.setter
    def model(self, value: bool):
        """The widget's model"""
        self.__checkbox.model.set_value(value)

    def _on_value_changed(self, *args):
        """Swap checkbox images and set revert_img to correct state."""
        self.__first_opt.checked = not self.__first_opt.checked
        self.__first_opt.name = "Toggle_ON_L" if self.__first_opt.checked else "Toggle_OFF_L"
        self.__first_opt_rect.name = "Toggle_ON_L" if self.__first_opt.checked else "Toggle_OFF_L"

        # The value of this depends on if the first option is checked or not
        self.model = self.__first_opt.checked
        
        # Second option relies on the first option
        self.__second_opt.checked = not self.__first_opt.checked
        self.__second_opt.name = "Toggle_ON_R" if self.__second_opt.checked else "Toggle_OFF_R"
        self.__second_opt_rect.name = "Toggle_ON_R" if self.__second_opt.checked else "Toggle_OFF_R"
        
        self.revert_img.enabled = self.__default_val != self.__first_opt.checked

    def _restore_default(self):
        """Restore the default value."""
        if self.revert_img.enabled:
            self.__first_opt.checked = self.__default_val
            self.__first_opt.name = "Toggle_ON_L" if self.__first_opt.checked else "Toggle_OFF_L"
            self.__first_opt_rect.name = "Toggle_ON_L" if self.__first_opt.checked else "Toggle_OFF_L"

            self.model = self.__first_opt.checked

            self.__second_opt.checked = not self.__first_opt.checked
            self.__second_opt.name = "Toggle_ON_R" if self.__second_opt.checked else "Toggle_OFF_R"
            self.__second_opt_rect.name = "Toggle_ON_R" if self.__second_opt.checked else "Toggle_OFF_R"

            self.revert_img.enabled = False

    def _build_body(self):
        """Build the Widget."""

        ui.Spacer()
        with ui.HStack(height=0, width=ui.Percent(TOGGLE_BUTTON_WIDTH_PERCENT)):
            # Creates spacing between label and item

            with ui.ZStack(height=25):
                self.__checkbox = ui.CheckBox(model=self.__selection_model, name="invisible_checkbox")

                self.__first_opt_rect = ui.Rectangle(name="Toggle_ON_L")
                self.__first_opt = ui.Label(
                    self.__first_option,
                    alignment=ui.Alignment.CENTER,
                    name="Toggle_ON",
                    checked=self.__default_val,
                )

            with ui.ZStack(height=25):
                self.__second_opt_rect = ui.Rectangle(name="Toggle_OFF_R")
                self.__second_opt = ui.Label(
                    self.__second_option,
                    alignment=ui.Alignment.CENTER,
                    name="Toggle_OFF",
                    checked=not self.__default_val,
                )

            self.__first_opt.set_mouse_pressed_fn(lambda x, y, b, m: self._on_value_changed())
            self.__second_opt.set_mouse_pressed_fn(lambda x, y, b, m: self._on_value_changed())
