"""Test definition file explorer.

This module provides helper methods to load files.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog

if TYPE_CHECKING:
    from gui.main_window import NewMainWindow
from control.controller import Controller


def open_file_dialog(self: NewMainWindow, controller: Controller) -> None:
    """Show a file dialog to select a sequence file."""
    # Open a file dialog and get the selected file path
    file_path_str, _ = QFileDialog.getOpenFileName(self, "Open File", "", "*.csv")
    file_path = Path(file_path_str)
    if file_path:
        self.label_sequence_file_name.setText(f"Selected file: {file_path}")
        controller.load_test_definition(file_path)
    else:
        self.label_sequence_file_name.setText("No file selected.")


def reload_file(self: NewMainWindow, controller: Controller) -> None:
    """Reload the same filename again."""
    controller.load_test_definition(self.label_sequence_file_name.text())
