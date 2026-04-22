"""UI update function.

This module provides methods to update ui elements
"""

from __future__ import annotations

from shared.state import telemetry, telemetry_lock
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from gui.main_window import NewMainWindow

import logging
import queue
from queue import Queue

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

import time
from control.definitions import EventType, State

logger = logging.getLogger(__name__)

from collections import deque

# TELEMETRY and Graphs

def update_telemetry(self: NewMainWindow):
    _pull_telemetry_to_local_history(self)
    _update_valve_labels(self)
    _refresh_plot_curves(self)


import time
from collections import deque
from shared.state import telemetry, telemetry_lock


def _pull_telemetry_to_local_history(self: "NewMainWindow"):
    with telemetry_lock:
        snapshot = telemetry.copy()

    t0 = self.controller.t0_wall

    for name, (ts, val) in snapshot.items():
        if name not in self.local_history:
            self.local_history[name] = {
                "time": deque(maxlen=self.max_points),
                "val": deque(maxlen=self.max_points),
                "last_ts": 0
            }

        #print(f"Pulled {name}, ts={ts}, val={val} to local history")

        hist = self.local_history[name]

        # TODO Nur neue Punkte? Pro Kontra Abwaegung
        if ts > hist["last_ts"]:
            rel_time = ts - t0

            hist["time"].append(rel_time)
            hist["val"].append(val)
            hist["last_ts"] = ts

def _update_valve_labels(self: NewMainWindow):
    """Update the state of every valve.

    This updates the text in the UI where the user can see
    the current position of the valve.
    """
    valve_mapping = {
        "main_valve_sensor": self.label_valve_status_main_state,
        "fill_valve_sensor": self.label_valve_status_fill_state,
        "vent_valve_sensor": self.label_valve_status_vent_state,
        "purge_valve_sensor": self.label_valve_status_purge_state,
        "pressurization_valve_sensor": self.label_valve_status_pressurization_state,
    }

    for sensor_name, label in valve_mapping.items():
        hist = self.local_history.get(sensor_name)
        if hist and hist["val"]:
            last_value = hist["val"][-1]
            #TODO von state nicht werte abhaenigig machen
            is_open = last_value > 0
            label.setText("OPEN" if is_open else "CLOSED")
            color = "#8FF0A4" if is_open else "#FFA0A0"
            label.setStyleSheet(f"color: {color}; font-weight: bold;")

def _refresh_plot_curves(self: NewMainWindow):
    # Aktuelle Zeit für das synchrone Scrolling
    # TODO Revisitg auto scrolling and scaling

    curve_mapping = {

        # pressure_tank temp_ox
        # load_cell_ox  load_cell_thrust
        # pressure_n2_bottle pressure_ox_bottle
        # pressure_cc_pre pressure_cc0

        # Nicht
        # pressure_cc1 temp_engine
        "pressure_tank": (self.pressure_curve_0, self.plot_pressure_0),
        "temp_ox": (self.pressure_curve_1, self.plot_pressure_1),
        "load_cell_ox": (self.pressure_curve_2, self.plot_pressure_2),
        "load_cell_thrust": (self.differential_pressure_curve, self.plot_differential_pressure),
        "pressure_n2_bottle": (self.load_cell_thrust_curve, self.plot_load_cell_thrust),
        "pressure_ox_bottle": (self.load_cell_ox_curve, self.plot_load_cell_nitrous),
        "pressure_cc_pre": (self.thermocouple_nitrous_curve, self.plot_thermocouple_nitrous),
        "pressure_cc0": (self.thermocouple_engine_curve, self.plot_thermocouple_engine),
    }

    now_abs = self.controller.t0_wall + (time.perf_counter() - self.controller.t0_perf)
    now_rel = now_abs - self.controller.t0_wall
    window = self.history_window_seconds

    for key, (curve, plot_widget) in curve_mapping.items():
        hist = self.local_history.get(key)
        if not hist or not hist["time"]:
            continue

        x = list(hist["time"])
        y = list(hist["val"])

        curve.setData(x, y)
        plot_widget.setXRange(now_rel - window, now_rel, padding=0)

def clear_data_cache(self: NewMainWindow) -> None:
    self.local_history = {}

# From here on SIGNAL-BASED
def _get_event_from_queue(event_queue: Queue) -> dict | None:
    """Get the event from the queue."""
    try:
        # set waiting to false
        event: dict = event_queue.get(False)
        logger.debug("received event %event", event)
        return event
    except queue.Empty:
        # queue is empty, Nothing to do.
        return None

def update_ui(self: NewMainWindow) -> None:  # noqa: C901
    """Update the plots with new sensor values."""
    event: dict = _get_event_from_queue(self.event_queue)
    if event is None:
        return

    match event["type"]:
        case EventType.CONNECTION_STATUS_UPDATE:
            update_connection_state(self, event)
        case EventType.SEQUENCE_STARTED:
            update_sequence_state(self, enabled=False)
            clear_data_cache(self)
        case EventType.SEQUENCE_STOPPED:
            update_sequence_state(self, enabled=True)
        case EventType.SEQUENCE_ERROR:
            show_sequence_error(self, event)
        case EventType.INFO_EVENT:
            show_info_event(self, event)
        case EventType.CONFIRMATION_EVENT:
            show_confirmation_event(self, event)
        case EventType.STATE_CHANGE:
            update_state(self, event)
        case EventType.ARMING_STATE_CHANGE:
            update_arming_state(self, event)
        case EventType.RESET_PLOTS:
            reset_plots(self)

def update_connection_state(self: NewMainWindow, connection_event: dict) -> None:
    """Update the labels to display the current connection status."""
    print("update the connection state in the GUI")
    self.label_status_connection_state.setText(connection_event["status"])
    self.label_status_hostname_state.setText(connection_event["hostname"])
    self.label_status_port_state.setText(str(connection_event["port"]))
    if connection_event["status"] == "Connected":
        self.button_connect.setText("Disconnect")
    elif connection_event["status"] == "Disconnected":
        self.button_connect.setText("Connect")

def update_sequence_state(self: NewMainWindow, *, enabled: bool) -> None:
    """Enable and disable the buttons to start a sequence or do abort a sequence."""
    # disable/enable start sequence button
    self.button_start_sequence.setEnabled(enabled)
    self.button_connect.setEnabled(enabled)

    self.button_selfcheck.setEnabled(enabled)
    self.button_test_horn.setEnabled(enabled)

    self.button_open_sequence.setEnabled(enabled)
    self.button_reload_sequence.setEnabled(enabled)

    self.button_abort_sequence.setEnabled(not enabled)

def update_state(self: NewMainWindow, event: dict) -> None:
    """Update the displayed state in the UI.

    Some actions are restricted to the red state and the user has to
    enter that state before he can press some buttons.
    This method does the state transition in the ui.
    """
    match event["new_state"]:
        case State.GREEN_STATE:
            self.group_state_green.setStyleSheet(
                "background-color: rgb(143, 240, 164);",
            )

            self.group_state_yellow.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )
            self.group_state_red.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )
        case State.YELLOW_STATE:
            self.group_state_yellow.setStyleSheet(
                "background-color: rgb(249, 240, 107);",
            )

            self.group_state_green.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )
            self.group_state_red.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )
        case State.RED_STATE:
            self.group_state_red.setStyleSheet(
                "background-color: rgb(255, 160, 160);",
            )

            self.group_state_yellow.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )
            self.group_state_green.setStyleSheet(
                "background-color: rgb(255, 255, 255);",
            )

def update_arming_state(self: NewMainWindow, event: dict) -> None:
    """Update the state of the arming buttons.

    Some buttons can only be pressed when we are in a armed state.
    This requires that the arming button is pressed before.
    """
    match event["new_state"]:
        case True:
            self.button_run_purge_sequence.setEnabled(True)
            self.button_run_ignition_sequence.setEnabled(True)
            self.button_toggle_purge_valve.setEnabled(True)
            self.button_toggle_pressurization_valve.setEnabled(True)
            self.button_toggle_main_valve.setEnabled(True)
            self.button_start_sequence.setEnabled(True)
        case False:
            self.button_run_purge_sequence.setEnabled(False)
            self.button_run_ignition_sequence.setEnabled(False)
            self.button_toggle_purge_valve.setEnabled(False)
            self.button_toggle_pressurization_valve.setEnabled(False)
            self.button_toggle_main_valve.setEnabled(False)
            self.button_start_sequence.setEnabled(False)

# MISC
def reset_plots(self: NewMainWindow) -> None:
    """Reset the plots in the UI.

    This in useful when the sensors are calibrated to remove the old plots.
    """
    self.load_cell_ox_curve.clear()
    self.load_cell_thrust_curve.clear()

def show_info_event(self: NewMainWindow, info_event: dict) -> None:
    """Show a dialog with an error message.

    If something went wrong, we can show the user a dialog with the error message.
    """
    # @TODO(Nucleus): redesign with pyside designer
    dlg = QDialog(self)
    dlg.setWindowTitle(info_event["title"])
    message = QLabel(info_event["message"])
    layout = QVBoxLayout()
    layout.addWidget(message)
    dlg.setLayout(layout)
    dlg.exec()

def show_confirmation_event(self: NewMainWindow, confirmation_event: dict) -> None:
    """Show a dialog with a confirmation request.

    This allows to have state transition a confirmation to change the state.
    """
    dlg = QDialog(self)
    dlg.setWindowTitle(confirmation_event["title"])
    message = QLabel(confirmation_event["message"])
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(confirmation_event["confirm"])
    button_box.accepted.connect(dlg.accept)
    button_box.rejected.connect(confirmation_event["cancel"])
    button_box.rejected.connect(dlg.reject)
    layout = QVBoxLayout()
    layout.addWidget(message)
    layout.addWidget(button_box)
    dlg.setLayout(layout)
    dlg.exec()

def show_sequence_error(self: NewMainWindow, error_event: dict) -> None:
    """Show a dialog with an error message."""
    # @TODO(Nucleus): redesign with pyside designer
    dlg = QDialog(self)
    dlg.setWindowTitle("something went wrong")
    message = QLabel(error_event["message"])
    layout = QVBoxLayout()
    layout.addWidget(message)
    dlg.setLayout(layout)
    dlg.exec()
