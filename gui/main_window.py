from curses.ascii import controlnames

from PySide6.QtCore import QTimer
from PySide6.QtUiTools import loadUiType
from PySide6.QtGui import QShortcut, QKeySequence
import pyqtgraph as pg

from control.controller import Controller
from .test_definition_file_explorer import (open_file_dialog, reload_file)
from .data_plotter import update_plots
from gui.ui_updater import update_ui

ui_class, baseclass = loadUiType("gui/main_view.ui")

class NewMainWindow(ui_class, baseclass):
    def __init__(self,
                 event_queue,
                 controller):
        super().__init__()
        self.showMaximized()

        self.event_queue = event_queue
        self.controller:Controller = controller

        # used to store the values from the queue
        self.pressure_0_data = []
        self.pressure_1_data = []
        self.pressure_2_data = []
        self.differential_pressure_data = []

        self.temperature_1_data = []
        self.temperature_2_data = []

        self.load_cell_1_data = []
        self.load_cell_2_data = []


        # @TODO how to handle the time?
        self.time_data = []

        self.setupUi(self)
        self.setup_graphs()
        self.setup_buttons()
        self.setup_shortcuts()

        # create plot curves
        self.pressure_curve_0 = self.plot_pressure_0.plot([], [], pen=pg.mkPen(color="r", width=1.5))
        self.pressure_curve_1 = self.plot_pressure_1.plot([], [], pen=pg.mkPen(color="g", width=1.5))
        self.pressure_curve_2 = self.plot_pressure_2.plot([], [], pen=pg.mkPen(color="b", width=1.5))
        self.differential_pressure_curve = self.plot_differential_pressure.plot([], [],
                                                                                pen=pg.mkPen(color="m", width=2))

        self.thermocouple_engine_curve = self.plot_thermocouple_engine.plot([], [], pen=pg.mkPen(color="c", width=2))
        self.thermocouple_nitrous_curve = self.plot_thermocouple_nitrous.plot([], [], pen=pg.mkPen(color="y", width=2))

        self.load_cell_nitrous_curve = self.plot_load_cell_nitrous.plot([], [], pen=pg.mkPen(color="brown", width=2))
        self.load_cell_thrust_curve = self.plot_load_cell_thrust.plot([], [], pen=pg.mkPen(color="w", width=2))

        # setup timer - used to update the plots
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_plots(self))
        self.timer.start(1000) # @TODO with 200, the UI beginns to get laggy

        self.event_timer = QTimer()
        self.event_timer.timeout.connect(lambda: update_ui(self))
        self.event_timer.start(1000)


    def setup_shortcuts(self):
        open_n2o_vent_valve_shortcut = QShortcut(QKeySequence("v"), self)
        open_n2o_vent_valve_shortcut.activated.connect(self.controller.open_as_long_pressed_n2o_vent_valve)

        open_n2_purge_valve_shortcut = QShortcut(QKeySequence("esc"), self)
        open_n2_purge_valve_shortcut.activated.connect(self.controller.open_as_long_pressed_n2_purge_valve)

    def setup_buttons(self):
        """
        Connect the click of a buttons to a methode
        """
        # Connection handler
        self.button_connect.clicked.connect(lambda: self.controller.connect(self.edit_host.text(),
                                                                            int(self.edit_port.text())))

        # Preparation
        self.button_selfcheck.clicked.connect(lambda: self.controller.self_check())

        self.button_toggle_sensors.clicked.connect(lambda: self.controller.toggle_sensors())
        self.button_test_counter.clicked.connect(lambda: self.controller.test_counter())

        self.button_calibrate_thrust_load.clicked.connect(lambda: self.controller.calibrate_thrust_load(self.edit_calibrate_load.text()))
        self.button_calibrate_nitrous_load.clicked.connect(lambda: self.controller.calibrate_nitrous_load(self.edit_calibrate_load.text()))

        # green state
        self.button_green_state.clicked.connect(lambda: self.controller.request_go_to_green_state())
        self.button_dump_sensors_to_file.clicked.connect(lambda: self.controller.dump_sensors_to_file())
        self.button_reset_sensors.clicked.connect(lambda: self.controller.reset_sensors())

        # yellow state
        self.button_yellow_state.clicked.connect(lambda: self.controller.request_go_to_yellow_state())

        # red state
        self.button_red_state.clicked.connect(lambda: self.controller.request_go_to_red_state())
        self.button_close_all_valves.clicked.connect(lambda: self.controller.close_all_valves())
        self.button_test_horn.clicked.connect(lambda: self.controller.test_horn())

        self.button_toggle_n2o_main_valve.clicked.connect(lambda: self.controller.toggle_n2o_main_valve())
        self.button_toggle_n2o_fill_valve.clicked.connect(lambda: self.controller.toggle_n2o_fill_valve())
        self.tool_button_open_n2o_vent_valve.clicked.connect(lambda: self.controller.open_n2o_vent_valve())
        self.button_toggle_n2_purge_valve.clicked.connect(lambda: self.controller.toggle_n2_purge_valve())
        self.button_toggle_n2_pressure_valve.clicked.connect(lambda: self.controller.toggle_n2_pressure_valve())
        self.button_toggle_quick_disconnect.clicked.connect(lambda: self.controller.toggle_quick_disconnect())


        self.button_run_n20_purge_sequence.clicked.connect(lambda: self.controller.run_n2o_purge_sequence())
        self.button_run_ignition_sequence.clicked.connect(lambda: self.controller.run_ignition_sequence())
        #self.button_open_vent_valve.


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
        self.plot_pressure_0.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_0.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_0.setLabel('left', 'Pressure 0 (bar)', color='#FFFFFF')

        self.plot_pressure_1.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_1.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_1.setLabel('left', 'Pressure 1 (bar)', color='#FFFFFF')

        self.plot_pressure_2.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_2.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_pressure_2.setLabel('left', 'Pressure 2 (bar)', color='#FFFFFF')

        # plot_differential_pressure
        self.plot_differential_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_differential_pressure.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_differential_pressure.setLabel('left', 'Differential Pressure (bar)', color='#FFFFFF')

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
        self.plot_load_cell_nitrous.setLabel('left', 'Load Cell Nitrous Tank (Kg)', color='#FFFFFF')

        self.plot_load_cell_thrust.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_thrust.setLabel('bottom', 'Time (ms)', color='#FFFFFF')
        self.plot_load_cell_thrust.setLabel('left', 'Load Cell Thrust (Kg)', color='#FFFFFF')
