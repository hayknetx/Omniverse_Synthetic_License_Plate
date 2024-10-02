from typing import List, Optional

import omni.ui as ui

from .lpsdg_base_widget import CustomBaseWidget
from smartcow.ext.lp_sdg.style import BLOCK_HEIGHT

COMBOBOX_WIDTH_PERCENT = 30


class CustomComboboxWidget(CustomBaseWidget):
    """A customized combobox widget"""

    def __init__(self, model: ui.AbstractItemModel = None, options: List[str] = None, default_value=0, **kwargs):
        self.__default_val = default_value
        self.__options = options or ["1", "2", "3"]
        self.__combobox_widget = None

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__options = None
        self.__combobox_widget = None

    @property
    def model(self) -> Optional[ui.AbstractItemModel]:
        """The widget's model"""
        if self.__combobox_widget:
            return self.__combobox_widget.model

    @model.setter
    def model(self, value: ui.AbstractItemModel):
        """The widget's model"""
        self.__combobox_widget.model = value

    def _on_value_changed(self, *args):
        """Set revert_img to correct state."""
        model = self.__combobox_widget.model
        index = model.get_item_value_model().get_value_as_int()
        self.revert_img.enabled = self.__default_val != index

    def _restore_default(self):
        """Restore the default value."""
        if self.revert_img.enabled:
            self.__combobox_widget.model.get_item_value_model().set_value(self.__default_val)
            self.revert_img.enabled = False

    def _build_body(self):
        """Main meat of the widget.  Draw the Rectangle, Combobox, and
        set up callbacks to keep them updated.
        """
        ui.Spacer()

        # Basic ComboBox! Not much changes here tbh other than styling options and default value setting
        # TODO: Add custom arrow?
        with ui.HStack(width=ui.Percent(COMBOBOX_WIDTH_PERCENT)):
            with ui.ZStack():
                option_list = list(self.__options)
                self.__combobox_widget = ui.ComboBox(
                    0,
                    *option_list,
                    height=BLOCK_HEIGHT,
                    name="dropdown_menu",
                )

        # Detect when value's been changed
        self.__combobox_widget.model.add_item_changed_fn(self._on_value_changed)
