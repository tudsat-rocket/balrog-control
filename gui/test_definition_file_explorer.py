from PySide6.QtWidgets import QFileDialog
from control.test_definition_parsing import parse_csv

def open_file_dialog(self):
    """
    Show a file dialog to select a sequence file
    """
    # Open a file dialog and get the selected file path
    file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "*.csv")
    if file_path:
        # @TODO parse the CSV and create stuff from that
        result = parse_csv(file_path)
        print(result)
        self.label_sequence_file_name.setText(f"Selected file: {file_path}")
    else:
        self.label_sequence_file_name.setText("No file selected.")


def reload_file(self):
    """
    Reload the same filename again
    """
    # @TODO implement
    result = parse_csv(self.label_sequence_file_name.text())
    print(result)