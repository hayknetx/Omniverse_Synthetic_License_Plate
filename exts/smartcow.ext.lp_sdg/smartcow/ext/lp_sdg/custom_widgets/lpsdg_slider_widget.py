from typing import Optional

import omni.ui as ui

from .lpsdg_base_widget import CustomBaseWidget

SLIDER_WIDTH = ui.Percent(70)
SLIDER_HEIGHT = 18

class CustomSliderWidget(CustomBaseWidget):
    """
    A widget for scalar slider input.
    """

    def __init__(self,
                 model: ui.AbstractItemModel = None,
                 num_type: str = "float",
                 min=0.0,
                 max=1.0,
                 default_val=0.0,
                 **kwargs):
        self.__slider: Optional[ui.AbstractSlider] = None
        self.__min = min
        self.__max = max
        self.__default_val = default_val
        self.__num_type = num_type

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__slider = None

    @property
    def model(self) -> Optional[ui.AbstractItemModel]:
        """ The widget's model. """
        if self.__slider:
            return self.__slider.model

    @model.setter
    def model(self, value: ui.AbstractItemModel):
        """ The widget's model. """
        self.__slider.model = value

    def _on_value_changed(self, *args):
        """ Set revert_img to correct state. """
        if self.__num_type == "float":
            index = self.model.as_float
        else:
            index = self.model.as_int
        self.revert_img.enabled = self.__default_val != index

    def _restore_default(self):
        """ Restore the default value. """
        if self.revert_img.enabled:
            self.model.set_value(self.__default_val)
            self.revert_img.enabled = False

    def _build_body(self):
        """ Build the Widget. """
        with ui.HStack():
            # Creates spacing between label and item
            ui.Spacer()

            with ui.HStack(width=ui.Percent(SLIDER_WIDTH), height=SLIDER_HEIGHT):
                # Slider definition
                slider_cls = (
                    ui.FloatSlider if self.__num_type == "float" else ui.IntSlider
                )

                # Slider instantiation
                self.__slider = slider_cls(
                    min=self.__min, max=self.__max, name="customslider"
                )
                
                # Setting defaults
                model = self.__slider.model
                model.set_value(self.__default_val)

        model.add_value_changed_fn(self._on_value_changed)