from ctypes import Union
from typing import List, Optional

import omni.ui as ui

from .lpsdg_base_widget import CustomBaseWidget

COLOR_PICKER_WIDTH = 25
COLOR_PICKER_HEIGHT = 18
COLOR_WIDGET_WIDTH_PERCENT = 50
COLOR_WIDGET_NAME = "color_block"
SPACING = 4


class CustomColorWidget(CustomBaseWidget):
    """The compound widget for color input. The color picker widget model converts
    its 3 RGB values into a comma-separated string, to display in the StringField.
    And vice-versa.
    """

    def __init__(self, *args, model=None, **kwargs):
        self.__defaults: List[Union[float, int]] = [a for a in args if a is not None]
        self.__colorpicker: Optional[ui.ColorWidget] = None
        self.__multifields = []
        self.__color_sub = None
        self.__multifield_subs = [None, None, None]
        self.__labels = ["R: ", "G: ", "B: "]

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__colorpicker = None

    @property
    def model(self) -> Optional[ui.AbstractItemModel]:
        """The widget's model"""
        if self.__colorpicker:
            return self.__colorpicker.model

    @model.setter
    def model(self, value: ui.AbstractItemModel):
        """The widget's model"""
        self.__colorpicker.model = value

    def set_multifield_values(self, item_model: ui.AbstractItemModel, children: List[ui.AbstractItem]):
        """Take the colorpicker model that has 3 child RGB values,
        convert them to a 0-255 int, and set the IntField values
        to that value.
        Args:
            item_model: Colorpicker model
            children: child Items of the colorpicker
        """

        # Set the colour from the int values
        for idx, model in enumerate(children):
            self.__multifields[idx].model.as_int = int(item_model.get_item_value_model(model).as_float * 255)

            if self.revert_img:
                self._on_value_changed(self.__multifields[idx].model, idx)

    def set_color_widget(self, children: List[ui.AbstractItem]):
        """Parse the new Multifields valuea and set the ui.ColorWidget
        component items to the new values.
        Args:
            int_model: SimpleIntModel for the IntFields
            children: Child Items of the ui.ColorWidget's model
        """

        # Set the colour from the int values
        for idx, model in enumerate(children):
            try:
                self.__colorpicker.model.get_item_value_model(model).as_float = (
                    float(self.__multifields[idx].model.as_int) / 255.0
                )
            except ValueError:
                # Usually happens in the middle of typing
                pass

    def _on_value_changed(self, val_model: ui.SimpleIntModel, index: int):
        """Set revert_img to correct state."""
        val = val_model.as_float
        self.revert_img.enabled = self.__defaults[index] != val

    def _restore_default(self):
        """Restore the default values."""
        if self.revert_img.enabled:
            # Revert ALL Int Field values

            for i in range(len(self.__multifields)):
                model = self.__multifields[i].model
                model.as_int = int(self.__defaults[i] * 255)

            self.revert_img.enabled = False

    def _build_body(self):
        """Main meat of the widget.  Draw the colorpicker and
        set up callbacks to keep them updated.
        """

        # Creates right-based spacing
        ui.Spacer()

        with ui.HStack(spacing=SPACING, width=ui.Percent(COLOR_WIDGET_WIDTH_PERCENT)):
            # The construction of the widget depends on what the user provided,
            # defaults or a model
            if self.existing_model:
                # the user provided a model
                self.__colorpicker = ui.ColorWidget(self.existing_model, width=COLOR_PICKER_WIDTH, name=COLOR_WIDGET_NAME)
                color_model = self.existing_model
            else:
                # the user provided a list of default values
                self.__colorpicker = ui.ColorWidget(*self.__defaults, width=COLOR_PICKER_WIDTH, name=COLOR_WIDGET_NAME)

                color_model = self.__colorpicker.model

            ui.Spacer(width=SPACING)

            # Initialize the Interger
            for idx, val in enumerate(self.__defaults):
                with ui.HStack():
                    # ui.Label(self.__labels[idx], name="multi_attr_label", width=0)

                    model = ui.SimpleIntModel(int(val * 255))

                    self.__multifields.append(
                        ui.IntDrag(model=model, min=0, max=255, height=COLOR_PICKER_HEIGHT, name="intdrag")
                    )

                    ui.Spacer(width=SPACING)

            # Change multifield values based on colour widget
            self.__color_sub = self.__colorpicker.model.subscribe_item_changed_fn(
                lambda m, _, children=color_model.get_item_children(): self.set_multifield_values(m, children)
            )

            # Change colour widget based on multifield values
            self.__multifield_subs = [field.model.subscribe_value_changed_fn(
                lambda _, children= color_model.get_item_children(): self.set_color_widget(children)
            ) for field in self.__multifields]

        # Initialize values
        self.set_multifield_values(self.__colorpicker.model, children=color_model.get_item_children())

        # Ensure following multifield changes
        for i, f in enumerate(self.__multifields):
            f.model.add_value_changed_fn(lambda v: self._on_value_changed(v, i))
