"""Module to provide the main GUI.

This module provide the main GUI.
"""

from queue import Queue

import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer
from PySide6.QtUiTools import loadUiType

from control.controller import Controller
from gui.ui_updater import update_ui, update_telemetry

from .test_definition_file_explorer import open_file_dialog, reload_file

ui_class, baseclass = loadUiType("gui/main_view.ui")


class NewMainWindow(ui_class, baseclass):
    """Main Window class.

    This represents the main window of the GUI.
    """

    def __init__(self, event_queue: Queue, controller) -> None:
        """Crate new window object.

        This creates a new main window object.
        This is the main window displayed to the user.
        """
        super().__init__()
        self.showMaximized()
        self.event_queue = event_queue
        self.controller: Controller = controller

        self.history_window_seconds = 20
        self.ui_refresh_time_ms = 50
        self.telemetry_refresh_time_ms = 100
        self.max_points = int(self.history_window_seconds * 1000 / self.telemetry_refresh_time_ms)
        self.local_history = {}

        self.setupUi(self)
        self.setup_graphs()
        self.setup_buttons()
        self.setup_plots()
        self.setup_timers()

    #TODO Warnings
    def setup_plots(self):
        # create plot curves
        self.pressure_curve_0 = self.plot_pressure_0.plot(
            [], [], pen=pg.mkPen(color="r", width=1.5)
        )
        self.pressure_curve_1 = self.plot_pressure_1.plot(
            [], [], pen=pg.mkPen(color="g", width=1.5)
        )
        self.pressure_curve_2 = self.plot_pressure_2.plot(
            [], [], pen=pg.mkPen(color="b", width=1.5)
        )
        self.differential_pressure_curve = self.plot_differential_pressure.plot(
            [], [], pen=pg.mkPen(color="m", width=2)
        )

        self.thermocouple_engine_curve = self.plot_thermocouple_engine.plot(
            [], [], pen=pg.mkPen(color="c", width=2)
        )
        self.thermocouple_nitrous_curve = self.plot_thermocouple_nitrous.plot(
            [], [], pen=pg.mkPen(color="y", width=2)
        )

        self.load_cell_ox_curve = self.plot_load_cell_nitrous.plot(
            [], [], pen=pg.mkPen(color="brown", width=2)
        )
        self.load_cell_thrust_curve = self.plot_load_cell_thrust.plot(
            [], [], pen=pg.mkPen(color="w", width=2)
        )

    # TODO Warnings
    def setup_timers(self):
        # Handles Plots, labels and deques
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_telemetry(self))
        self.timer.start(self.telemetry_refresh_time_ms)

        # Handles signal etc.
        self.event_timer = QTimer()
        self.event_timer.timeout.connect(lambda: update_ui(self))
        self.event_timer.start(self.ui_refresh_time_ms)

    def key_press_event(self, event) -> None:
        """Override the keypress handler to implement our shortcuts."""
        # implement v shortcut for opening the vent
        # valve as long as the key is pressed
        if event.key() == Qt.Key.Key_V and not event.isAutoRepeat():
            self.controller.toggle_vent_valve()
        # implement the esc shortcut for opening the purge
        # valve as long as the key us pressed
        elif event.key() == Qt.Key.Key_Escape and not event.isAutoRepeat():
            self.controller.toggle_purge_valve()

        super().key_press_event(event)

    def key_release_event(self, event) -> None:
        """Override the keyrelease handler to implement our shortcuts."""
        if event.key() == Qt.Key.Key_V and not event.isAutoRepeat():
            #self.controller.toggle_vent_valve()
            pass
        elif event.key() == Qt.Key.Key_Escape and not event.isAutoRepeat():
            #self.controller.toggle_purge_valve()
            pass
        super().key_release_event(event)

    def setup_buttons(self) -> None:
        """Connects Buttons with Controller"""
        ctrl = self.controller

        direct_map = {
            # System & Check
            self.button_selfcheck: ctrl.self_check,
            self.button_toggle_water: ctrl.toggle_vent_solenoid,
            self.button_test_counter: ctrl.test_counter,
            self.button_test_horn: ctrl.test_horn,
#            self.button_abort_sequence: ctrl.abort,
            # States
            self.button_green_state: ctrl.request_go_to_green_state,
            self.button_yellow_state: ctrl.request_go_to_yellow_state,
            self.button_red_state: ctrl.request_go_to_red_state,
            self.button_toggle_arming: ctrl.toggle_arming,
            # Maintenance
            self.button_dump_sensors_to_file: ctrl.toggle_fill_valve,
#            self.button_reset_sensors: ctrl.reset_sensors,
            self.button_close_all_valves: ctrl.close_all_valves,
            # Ventile & Aktoren
            self.button_toggle_main_valve: ctrl.toggle_main_valve,
#            self.button_toggle_fill_valve: ctrl.toggle_fill_valve,
            self.button_toggle_fill_valve: ctrl.toggle_fill_solenoid,
            self.button_toggle_vent_valve: ctrl.toggle_vent_valve,
            self.button_toggle_purge_valve: ctrl.toggle_purge_valve,
            self.button_toggle_pressurization_valve: ctrl.toggle_pressurization_valve,
            self.button_toggle_quick_disconnect_solenoid: ctrl.toggle_qd_solenoid,
            self.button_trigger_quick_disconnect: ctrl.trigger_qd,
            # Sequenzen
            self.button_run_purge_sequence: ctrl.run_purge_sequence,
            self.button_run_ignition_sequence: ctrl.request_run_ignition_sequence,
            self.button_start_sequence: ctrl.start_sequence,
        }

        for btn, method in direct_map.items():
            btn.clicked.connect(method)

        self.button_connect.clicked.connect(
            lambda: ctrl.connect(self.edit_host.text(), int(self.edit_port.text() or 0))
        )

        self.button_calibrate_thrust_load.clicked.connect(
            lambda: ctrl.calibrate_thrust_load(self.edit_calibrate_load.text(), self.edit_calibrate_load.clear)
        )
        self.button_calibrate_ox_load.clicked.connect(
            lambda: ctrl.calibrate_ox_load(self.edit_calibrate_load.text(), self.edit_calibrate_load.clear)
        )

        self.button_open_sequence.clicked.connect(lambda: open_file_dialog(self, ctrl))
        self.button_reload_sequence.clicked.connect(lambda: reload_file(self, ctrl))

    def setup_graphs(self) -> None:
        """Define the labels and other settings for the graphs."""
        # pressure
        self.plot_pressure_0.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_0.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_pressure_0.setLabel("left", "Pressure Tank (bar)", color="#FFFFFF")
        self.plot_pressure_0.setAutoVisible(y=True)

        self.plot_pressure_1.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_1.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_pressure_1.setLabel("left", "Temp Ox (°C)", color="#FFFFFF")
        self.plot_pressure_1.setAutoVisible(y=True)

        self.plot_pressure_2.showGrid(x=True, y=True, alpha=0.3)
        self.plot_pressure_2.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_pressure_2.setLabel("left", "Load-cell Tank (kg)", color="#FFFFFF")
        self.plot_pressure_2.setAutoVisible(y=True)

        # plot_differential_pressure
        self.plot_differential_pressure.showGrid(x=True, y=True, alpha=0.3)
        self.plot_differential_pressure.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_differential_pressure.setLabel(
            "left",
            "Load-cell Thrust (kg)",
            color="#FFFFFF",
        )
        self.plot_differential_pressure.setAutoVisible(y=True)

        self.plot_load_cell_thrust.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_thrust.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_load_cell_thrust.setLabel(
            "left",
            "Pressure N2 Bottle (bar)",
            color="#FFFFFF",
        )
        self.plot_load_cell_thrust.setAutoVisible(y=True)

        # plot_load_cell
        self.plot_load_cell_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_load_cell_nitrous.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_load_cell_nitrous.setLabel(
            "left",
            "Pressure Ox Bottle (bar)",
            color="#FFFFFF",
        )
        self.plot_load_cell_nitrous.setAutoVisible(y=True)

        # plot_thermocouple
        self.plot_thermocouple_nitrous.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_nitrous.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_thermocouple_nitrous.setLabel(
            "left",
            "Pressure CC-Pre (bar)",
            color="#FFFFFF",
        )
        self.plot_thermocouple_nitrous.setAutoVisible(y=True)

        self.plot_thermocouple_engine.showGrid(x=True, y=True, alpha=0.3)
        self.plot_thermocouple_engine.setLabel("bottom", "Time (s)", color="#FFFFFF")
        self.plot_thermocouple_engine.setLabel(
            "left",
            "Pressure CC-0 (bar)",
            color="#FFFFFF",
        )
        self.plot_thermocouple_engine.setAutoVisible(y=True)
