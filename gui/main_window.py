from curses.ascii import controlnames

from PySide6.QtCore import QTimer
from PySide6.QtUiTools import loadUiType
import pyqtgraph as pg

from control.controller import Controller
from .test_definition_file_explorer import (open_file_dialog, reload_file)
from .data_plotter import update_plots
from gui.ui_updater import update_ui

ui_class, baseclass = loadUiType("gui/main_view.ui")

class NewMainWindow(ui_class, baseclass):
    def __init__(self,
                 pressure_1_sensor_queue,
                 pressure_2_sensor_queue,
                 pressure_3_sensor_queue,
                 pressure_4_sensor_queue,

                 temperature_1_sensor_queue,
                 temperature_2_sensor_queue,
                 load_cell_1_sensor_queue,
                 load_cell_2_sensor_queue,
                 differential_sensor_queue,
                 event_queue,
                 controller):
        super().__init__()

        # queue to transport the sensor values from the second thread to the UI
        self.pressure_1_sensor_queue = pressure_1_sensor_queue
        self.pressure_2_sensor_queue = pressure_2_sensor_queue
        self.pressure_3_sensor_queue = pressure_3_sensor_queue
        self.pressure_4_sensor_queue = pressure_4_sensor_queue
        self.temperature_1_sensor_queue = temperature_1_sensor_queue
        self.temperature_2_sensor_queue = temperature_2_sensor_queue
        self.load_cell_1_sensor_queue = load_cell_1_sensor_queue
        self.load_cell_2_sensor_queue = load_cell_2_sensor_queue
        self.differential_sensor_queue = differential_sensor_queue
        self.event_queue = event_queue
        self.controller = controller

        # used to store the values from the queue
        self.pressure_1_data = []
        self.pressure_2_data = []
        self.pressure_3_data = []
        self.pressure_4_data = []

        self.temperature_1_data = []
        self.temperature_2_data = []

        self.load_cell_1_data = []
        self.load_cell_2_data = []
        self.differential_pressure_data = []

        # @TODO how to handle the time?
        self.time_data = []

        self.setupUi(self)
        self.setup_graphs()
        self.setup_buttons()

        # create plot curves
        self.pressure_curve_1 = self.plot_pressure_1.plot([], [], pen=pg.mkPen(color="r", width=1.5))
        self.pressure_curve_2 = self.plot_pressure_2.plot([], [], pen=pg.mkPen(color="r", width=1.5))
        self.pressure_curve_3 = self.plot_pressure_3.plot([], [], pen=pg.mkPen(color="r", width=1.5))
        self.pressure_curve_4 = self.plot_pressure_4.plot([], [], pen=pg.mkPen(color="r", width=1.5))

        self.thermocouple_engine_curve = self.plot_thermocouple_engine.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.thermocouple_nitrous_curve = self.plot_thermocouple_nitrous.plot([], [], pen=pg.mkPen(color="r", width=2))

        self.load_cell_nitrous_curve = self.plot_load_cell_nitrous.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.load_cell_thrust_curve = self.plot_load_cell_thrust.plot([], [], pen=pg.mkPen(color="r", width=2))
        self.differential_pressure_curve = self.plot_differential_pressure.plot([], [], pen=pg.mkPen(color="r", width=2))

        # setup timer - used to update the plots
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_plots(self))
        self.timer.start(1000) # @TODO with 200, the UI beginns to get laggy

        self.event_timer = QTimer()
        self.event_timer.timeout.connect(lambda: update_ui(self))
        self.event_timer.start(1000)

    def setup_buttons(self):
        """
        Connect the click of a buttons to a methode
        """
        # Connection handler
        self.button_connect.clicked.connect(lambda: self.controller.connect(self.edit_host.text(),
                                                                            int(self.edit_port.text())))

        # Preparation
        self.button_selfcheck.clicked.connect(lambda: self.controller.self_check())
        self.button_test_horn.clicked.connect(lambda: self.controller.test_horn())
        self.button_test_light.clicked.connect(lambda: self.controller.test_light())
        self.button_toggle_sensors.clicked.connect(lambda: self.controller.toggle_sensors())

        # Sequence loader
        self.button_start_sequence.clicked.connect(lambda: self.controller.start_sequence())
        self.button_open_sequence.clicked.connect(lambda: open_file_dialog(self, self.controller))
        self.button_reload_sequence.clicked.connect(lambda: reload_file(self, self.controller))

        # Abort
        self.button_abort_sequence.clicked.connect(lambda: self.controller.abort())

    def setup_graphs(self):
        """
        define the labels and other settings for the graphs
        """
        # pressure
        self.plot_pressure_1.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_1.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_1.setLabel('left', 'Pressure 1 (bar)', color='#FFFFFF')

        self.plot_pressure_2.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_2.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_2.setLabel('left', 'Pressure 2 (bar)', color='#FFFFFF')

        self.plot_pressure_3.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_3.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_3.setLabel('left', 'Pressure 3 (bar)', color='#FFFFFF')

        self.plot_pressure_4.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_4.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_4.setLabel('left', 'Pressure 4 (bar)', color='#FFFFFF')

        # plot_thermocouple
        self.plot_thermocouple_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_nitrous.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_thermocouple_nitrous.setLabel('left', 'Temperature Nitrous (°C)', color='#FFFFFF')

        self.plot_thermocouple_engine.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_engine.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_thermocouple_engine.setLabel('left', 'Temperature Engine (°C)', color='#FFFFFF')

        # plot_load_cell
        self.plot_load_cell_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_nitrous.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell_nitrous.setLabel('left', 'Load Cell Nitrous Tank (N)', color='#FFFFFF')

        self.plot_load_cell_thrust.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_thrust.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell_thrust.setLabel('left', 'Load Cell Thrust (N)', color='#FFFFFF')

        # plot_differential_pressure
        self.plot_differential_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_differential_pressure.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_differential_pressure.setLabel('left', 'Differential Pressure (bar)', color='#FFFFFF')
