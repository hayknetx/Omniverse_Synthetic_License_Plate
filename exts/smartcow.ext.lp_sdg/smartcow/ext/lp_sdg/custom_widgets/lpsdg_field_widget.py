from typing import Optional

import omni.ui as ui
from omni.ui import color as cl
from omni.ui import constant as fl

from .lpsdg_base_widget import CustomBaseWidget

FIELD_WIDTH_PERCENT = 50
FIELD_HEIGHT = 18

class CustomFieldWidget(CustomBaseWidget):
    """A widget for a Field with text input."""

    def __init__(
        self,
        model: ui.AbstractItemModel = None,
        num_type: str = "float",
        tail_descriptor: str = "",
        default_val=0.0,
        min=0,
        max=10000,
        **kwargs
    ):
        self.__numberfield: Optional[ui.AbstractField] = None
        self.__default_val = default_val
        self.__num_type = num_type
        self.__tail_descriptor = tail_descriptor
        self.__min = min
        self.__max = max

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__numberfield = None

    @property
    def model(self) -> Optional[ui.AbstractItemModel]:
        """The widget's model"""
        if self.__numberfield:
            return self.__numberfield.model

    @model.setter
    def model(self, value: ui.AbstractItemModel):
        """The widget's model"""
        self.__numberfield.model = value

    def _on_value_changed(self, val_model: ui.SimpleFloatModel):
        """Set revert_img to correct state."""
        if self.__num_type == "float":
            index = val_model.as_float
        else:
            index = val_model.as_int
        self.revert_img.enabled = self.__default_val != index

    def _restore_default(self):
        """Restore the default value."""
        if self.revert_img.enabled:
            self.model.set_value(self.__default_val)
            self.revert_img.enabled = False

    def _build_body(self):
        """Main meat of the widget.  Draw the Slider, display range text, Field,
        and set up callbacks to keep them updated.
        """

        with ui.HStack(spacing=0):
            # Creates spacing between label and item
            ui.Spacer()

            with ui.HStack(width=ui.Percent(FIELD_WIDTH_PERCENT)):
                with ui.ZStack():
                    # Model definition
                    field_cls = ui.FloatDrag if self.__num_type == "float" else ui.IntDrag

                    # Model instantiation
                    self.__numberfield = field_cls(
                        height=FIELD_HEIGHT,
                        name="intdrag",
                        min=self.__min,
                        max=self.__max,
                    )

                    # Setting defaults
                    model = self.__numberfield.model
                    model.set_value(self.__default_val)

                if self.__tail_descriptor:
                    ui.Label(self.__tail_descriptor, name="field_tail")

        model.add_value_changed_fn(self._on_value_changed)
