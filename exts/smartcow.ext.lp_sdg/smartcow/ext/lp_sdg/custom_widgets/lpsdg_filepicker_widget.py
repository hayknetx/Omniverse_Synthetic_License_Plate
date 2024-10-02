from typing import Optional

import omni.ui as ui

import carb

import os

from typing import Callable, List
from omni.kit.window.popup_dialog import MessageDialog
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem

from .lpsdg_base_widget import CustomBaseWidget

FILEPICKER_WIDTH_PERCENT = 60
IMG_HEIGHT = 20
IMG_WIDTH = 20
SPACING = 4

class CustomFilePickerWidget(CustomBaseWidget):
    """
    A widget for filepicker input.
    """

    def __init__(self,
                 model: ui.AbstractItemModel = None,
                 filepath: str = None,
                 **kwargs):
        self._filepicker = None
        self._overwrite_warning_popup = None
        self._ui_kit_open_path = None

        self._filepicker_selected_folder = filepath

        # Call at the end, rather than start, so build_fn runs after all the init stuff
        CustomBaseWidget.__init__(self, model=model, **kwargs)

    def destroy(self):
        CustomBaseWidget.destroy()
        self._capture_instance = None
        self._filepicker = None
        self._ui_kit_open_path = None
        self._overwrite_warning_popup = None

    @property
    def model(self) -> Optional[ui.AbstractItemModel]:
        """ The widget's model. """
        if self._ui_kit_path:
            return self._ui_kit_path.model

    @model.setter
    def model(self, value: ui.AbstractItemModel):
        """ The widget's model. """
        self._ui_kit_path.model = value

    def _on_value_changed(self, *args):
        """ Set revert_img to correct state. """
        if self.__num_type == "float":
            index = self.model.as_float
        else:
            index = self.model.as_int
        
        # Revert defaults
        self.revert_img.enabled = self.__default_val != index

    def _restore_default(self):
        """ Restore the default value. """
        if self.revert_img.enabled:
            self.model.set_value(self.__default_val)
            self.revert_img.enabled = False

    def _build_body(self):
        """ Build the Widget. """
        ui.Spacer()

        with ui.HStack(width=ui.Percent(FILEPICKER_WIDTH_PERCENT)):
            # Creates spacing between label and item
            with ui.VStack():
                self._ui_kit_path = ui.StringField(name="stringfield")
                # default_dir = carb.tokens.get_tokens_interface().resolve("${shared_documents}/capture")
                self._ui_kit_path.model.set_value(self._filepicker_selected_folder)

            ui.Spacer(width=SPACING*2)

            with ui.HStack(width=0):
                with ui.VStack():
                    self._ui_kit_change_path = ui.Image(
                        name="select_dir",
                        height=IMG_HEIGHT,
                        width=IMG_WIDTH,
                        mouse_pressed_fn=lambda x, y, b, _: self.on_filepicker_btn_click(),
                    )

                ui.Spacer(width=SPACING*2)

                with ui.VStack():
                    self._ui_kit_open_path = ui.Image(
                        name="open_curr_dir",
                        height=IMG_HEIGHT,
                        width=IMG_WIDTH,
                        mouse_pressed_fn=lambda x, y, b, _: self._on_open_path_clicked(),
                    )

                ui.Spacer(width=SPACING*2)

    def _build_tail(self):
        # Get rid of 'default' option; we don't really care
        pass

    def on_filepicker_btn_click(self):
        """A callback to open the filesystem for path selection"""
        self._filepicker = FilePickerDialog(
            "Select Folder",
            show_only_collections="my-computer",
            apply_button_label="Select",
            item_filter_fn=lambda item: self._on_filepicker_filter_item(item),
            selection_changed_fn=lambda items: self._on_filepicker_selection_change(items),
            click_apply_handler=lambda filename, dirname: self._on_dir_pick(self._filepicker, filename, dirname),
        )

        self._filepicker.set_filebar_label_name("Folder Name: ")
        self._filepicker.refresh_current_directory()
        self._filepicker.show(self._ui_kit_path.model.get_value_as_string())

    def _on_filepicker_filter_item(self, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True
        return False

    def _on_filepicker_selection_change(self, items: List[FileBrowserItem] = []):
        last_item = items[-1]
        self._filepicker.set_filename(last_item.name)
        self._filepicker_selected_folder = last_item.path

    def _on_open_path_clicked(self):
        self._make_sure_dir_existed(self._ui_kit_path.model.as_string)
        path = os.path.realpath(self._ui_kit_path.model.as_string)
        os.startfile(path)

    def _build_overwrite_warning_popup(self, parent: ui.Widget = None) -> MessageDialog:
        message = "Do you really want to overwrite the existing image frames captured?"
        dialog = MessageDialog(
            parent=parent,
            message=message,
            ok_handler=self._on_overwrite_warn_popup_yes_clicked,
            cancel_handler=self._on_overwrite_warn_popup_no_clicked,
            ok_label="Yes",
            cancel_label="No, uncheck it"
        )
        return dialog

    def _make_sure_dir_existed(self, dir):
        if not os.path.exists(dir):
            try:
                os.makedirs(dir, exist_ok=True)
            except OSError as error:
                carb.log_warn(f"Output directory cannot be created: {dir}. Error: {error}")
                return False
        return True

    def _on_dir_pick(self, dialog: FilePickerDialog, filename: str, dirname: str):
        dialog.hide()
        self._ui_kit_path.model.set_value(self._filepicker_selected_folder)