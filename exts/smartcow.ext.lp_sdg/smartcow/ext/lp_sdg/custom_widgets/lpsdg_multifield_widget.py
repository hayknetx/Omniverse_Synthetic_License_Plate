from typing import List, Optional

import omni.ui as ui

from .lpsdg_base_widget import CustomBaseWidget

MULTIFIELD_WIDTH_PERCENT = 50
MULTIFIED_HEIGHT = 18


class CustomMultifieldWidget(CustomBaseWidget):
    """A custom multifield widget with a variable number of fields, and
    customizable sublabels.
    """

    def __init__(
        self,
        model: ui.AbstractItemModel = None,
        sublabels: Optional[List[str]] = None,
        default_vals: Optional[List[float]] = None,
        num_type="float",
        min=0,
        max=1000,
        **kwargs
    ):
        self.__field_labels = sublabels or ["X", "Y", "Z"]
        self.__default_vals = default_vals or [0.0] * len(self.__field_labels)
        self.__multifields = []
        self.__num_type = num_type
        self.__min_val = min
        self.__max_val = max

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self.__multifields = []

    @property
    def model(self, index: int = 0) -> Optional[ui.AbstractItemModel]:
        """The widget's model"""
        if self.__multifields:
            return self.__multifields[index].model

    @model.setter
    def model(self, value: ui.AbstractItemModel, index: int = 0):
        """The widget's model"""
        self.__multifields[index].model = value

    @property
    def multifields(self):
        if self.__multifields:
            return self.__multifields

    # NOTE: ADD MODELS AD INFINITUM HERE!
    @multifields.setter
    def multifields(self, *args):
        self.__multifields = [args]

    def _restore_default(self):
        """Restore the default values."""
        if self.revert_img.enabled:
            for i in range(len(self.__multifields)):
                model = self.__multifields[i].model
                if self.__num_type == "float":
                    model.as_float = self.__default_vals[i]
                else:
                    model.as_int = self.__default_vals[i]

            self.revert_img.enabled = False

    def _on_value_changed(self, index: int):
        """Set revert_img to correct state."""
        if self.__num_type == "float":
            val = self.model.as_float
        else:
            val = self.model.as_int

        self.revert_img.enabled = self.__default_vals[index] != val

    def _build_body(self):
        """Main meat of the widget.  Draw the multiple Fields with their
        respective labels, and set up callbacks to keep them updated.
        """
        ui.Spacer()

        with ui.HStack(width=ui.Percent(MULTIFIELD_WIDTH_PERCENT)):
            for i, (label, val) in enumerate(zip(self.__field_labels, self.__default_vals)):
                with ui.HStack(spacing=3):
                    ui.Label(label, name="multi_attr_label", width=0)

                    if self.__num_type == "float":
                        model = ui.SimpleFloatModel(val)
                        self.__multifields.append(
                            ui.FloatDrag(
                                model=model,
                                min=self.__min_val,
                                max=self.__max_val,
                                height=MULTIFIED_HEIGHT,
                                name="multifield_attr",
                            )
                        )
                    else:
                        model = ui.SimpleIntModel(val)
                        self.__multifields.append(
                            ui.IntDrag(
                                model=model,
                                min=self.__min_val,
                                max=self.__max_val,
                                height=MULTIFIED_HEIGHT,
                                name="multifield_attr",
                            )
                        )

                if i < len(self.__default_vals) - 1:
                    # Only put space between fields and not after the last one
                    ui.Spacer(width=15)

        for i, f in enumerate(self.__multifields):
            f.model.add_value_changed_fn(lambda v: self._on_value_changed(i))
