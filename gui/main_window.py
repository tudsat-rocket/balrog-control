from PySide6.QtCore import QTimer
import pyqtgraph as pg
from .test_definition_file_explorer import (open_file_dialog, reload_file)
from .data_plotter import update_plots

ui_class, baseclass = pg.Qt.loadUiType("gui/main_view.ui")

class NewMainWindow(ui_class, baseclass):
    def __init__(self, pressure_sensor_queue,
                 current_sensor_queue,
                 thermocouples_sensor_queue,
                 load_cell_sensor_queue,
                 differential_sensor_queue):
        super().__init__()

        # queue to transport the sensor values from the second thread to the UI
        self.pressure_sensor_queue = pressure_sensor_queue
        self.current_sensor_queue = current_sensor_queue
        self.thermocouples_sensor_queue = thermocouples_sensor_queue
        self.load_cell_sensor_queue = load_cell_sensor_queue
        self.differential_sensor_queue = differential_sensor_queue

        # used to store the values from the queue
        self.pressure_data = []
        self.current_data = []
        self.thermocouples_data = []
        self.load_cell_data = []
        self.differential_pressure_data = []

        # @TODO how to handle the time?
        self.time_data = []

        self.setupUi(self)
        self.setup_graphs()
        self.setup_buttons()

        # create plot curves
        self.pressure_curve_1 = self.plot_pressure.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.pressure_curve_2 = self.plot_pressure.plot([], [], pen=pg.mkPen(color="b", width=2))
        self.pressure_curve_3 = self.plot_pressure.plot([], [], pen=pg.mkPen(color="g", width=2))

        self.thermocouple_curve = self.plot_thermocouple.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.load_cell_curve = self.plot_load_cell.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.current_curve = self.plot_current.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.differential_pressure_curve = self.plot_differential_pressure.plot([], [], pen=pg.mkPen(color="r", width=2))

        # setup timer - used to update the plots
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_plots(self))
        self.timer.start(1000) # @TODO with 200, the UI beginns to get laggy

    @staticmethod
    def dummy_button_action(self, button_name):
        """Just for testing"""
        print(f" {button_name} pressed")
        pass

    def setup_buttons(self):
        """
        Connect the click of a buttons to a methode
        @TODO: replace placeholder action for buttons
        """
        # Connection handler
        self.button_connect.clicked.connect(lambda: self.dummy_button_action(self, "connect"))

        # Preparation
        self.button_selfcheck.clicked.connect(lambda: self.dummy_button_action(self, "selfcheck"))
        self.button_test_horn.clicked.connect(lambda: self.dummy_button_action(self, "test horn"))
        self.button_test_light.clicked.connect(lambda: self.dummy_button_action(self, "test light"))

        # Sequence loader
        self.button_open_sequence.clicked.connect(lambda: open_file_dialog(self))
        self.button_reload_sequence.clicked.connect(lambda: reload_file(self))
        self.button_start_sequence.clicked.connect(lambda: self.dummy_button_action(self, "start sequence"))

        # Abort
        self.button_abort_sequence.clicked.connect(lambda: self.dummy_button_action(self, "abort"))

    def setup_graphs(self):
        """
        define the labels and other settings for the graphs
        """
        # pressure
        self.plot_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure.setLabel('left', 'pressure', color='#FFFFFF')

        # plot_thermocouple
        self.plot_thermocouple.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_thermocouple.setLabel('left', 'Temperature', color='#FFFFFF')

        # plot_load_cell
        self.plot_load_cell.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell.setLabel('left', 'Load cell', color='#FFFFFF')

        # plot_current
        self.plot_current.showGrid(x=True, y=True, alpha=0.3)
        self.plot_current.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_current.setLabel('left', 'Current', color='#FFFFFF')

        # plot_differential_pressure
        self.plot_differential_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_differential_pressure.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_differential_pressure.setLabel('left', 'differential pressure', color='#FFFFFF')