from PySide6.QtWidgets import QFileDialog

from control.controller import Controller
from control.test_definition_parsing import parse_csv

def open_file_dialog(self, controller:Controller):
    """
    Show a file dialog to select a sequence file
    """
    # Open a file dialog and get the selected file path
    file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "*.csv")
    if file_path:
        self.label_sequence_file_name.setText(f"Selected file: {file_path}")
        controller.load_test_definition(file_path)
    else:
        self.label_sequence_file_name.setText("No file selected.")


def reload_file(self, controller:Controller):
    """
    Reload the same filename again
    """
    controller.load_test_definition(self.label_sequence_file_name.text())