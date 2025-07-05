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
        self.thermocouples_data = []
        self.load_cell_data = []
        self.differential_pressure_data = []

        # @TODO how to handle the time?
        self.time_data = []

        self.setupUi(self)
        self.setup_graphs()
        self.setup_buttons()

        # create plot curves
        self.pressure_curve_1 = self.plot_pressure_1.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.pressure_curve_2 = self.plot_pressure_2.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.pressure_curve_3 = self.plot_pressure_3.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.pressure_curve_4 = self.plot_pressure_4.plot([], [], pen=pg.mkPen(color="r", width=2))

        self.thermocouple_engine_curve = self.plot_thermocouple_engine.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.thermocouple_nitrous_curve = self.plot_thermocouple_nitrous.plot([], [], pen=pg.mkPen(color="r", width=2))

        self.load_cell_nitrous_curve = self.plot_load_cell_nitrous.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.load_cell_thrust_curve = self.plot_load_cell_thrust.plot([], [], pen=pg.mkPen(color="r", width=2))
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
        self.plot_pressure_1.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_1.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_1.setLabel('left', 'pressure 1', color='#FFFFFF')

        self.plot_pressure_2.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_2.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_2.setLabel('left', 'pressure 2', color='#FFFFFF')

        self.plot_pressure_3.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_3.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_3.setLabel('left', 'pressure 3', color='#FFFFFF')

        self.plot_pressure_4.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_4.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_4.setLabel('left', 'pressure 4', color='#FFFFFF')

        # plot_thermocouple
        self.plot_thermocouple_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_nitrous.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_thermocouple_nitrous.setLabel('left', 'Temperature nitrous', color='#FFFFFF')

        self.plot_thermocouple_engine.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_engine.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_thermocouple_engine.setLabel('left', 'Temperature engine', color='#FFFFFF')

        # plot_load_cell
        self.plot_load_cell_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_nitrous.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell_nitrous.setLabel('left', 'Load cell nitrous tank', color='#FFFFFF')

        self.plot_load_cell_thrust.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_thrust.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell_thrust.setLabel('left', 'Load cell thrust', color='#FFFFFF')

        # plot_differential_pressure
        self.plot_differential_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_differential_pressure.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_differential_pressure.setLabel('left', 'differential pressure', color='#FFFFFF')