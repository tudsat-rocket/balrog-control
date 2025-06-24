import sys 
from gui.ui import MainWindow
from PySide6.QtWidgets import QApplication

def start_main_window():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start_main_window()

