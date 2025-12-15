"""UI update function.

This module provides methods to update ui elements
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.main_window import NewMainWindow

import logging
import queue
from queue import Queue

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from control.definitions import EventType, State
from shared.shared_lists import (
    n2_pressure_valve_sensor_list,
    n2_purge_valve_sensor_list,
    n2o_fill_valve_sensor_list,
    n2o_main_valve_sensor_list,
    n2o_vent_valve_sensor_list,
)

logger = logging.getLogger(__name__)


def read_events_values_from_queue(self: NewMainWindow) -> None:
    """Consume the newest values from the sensor queues."""
    # get new pressure value from queue
    self.eventdata.append()


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


def update_valve_states(self: NewMainWindow) -> None:
    """Update the state of every valve.

    This updates the text in the UI where the user can see
    the current position of the valve.
    """
    if len(n2o_main_valve_sensor_list[1]) > 0:
        state = n2o_main_valve_sensor_list[1][-1]
        self.label_valve_status_n2o_main_state.setText(str(state))
    if len(n2o_fill_valve_sensor_list[1]) > 0:
        state = n2o_fill_valve_sensor_list[1][-1]
        self.label_valve_status_n2o_fill_state.setText(str(state))
    if len(n2o_vent_valve_sensor_list[1]) > 0:
        state = n2o_vent_valve_sensor_list[1][-1]
        self.label_valve_status_n2o_vent_state.setText(str(state))
    if len(n2_purge_valve_sensor_list[1]) > 0:
        state = n2_purge_valve_sensor_list[1][-1]
        self.label_valve_status_n2_purge_state.setText(str(state))
    if len(n2_pressure_valve_sensor_list[1]) > 0:
        state = n2_pressure_valve_sensor_list[1][-1]
        self.label_valve_status_n2_pressure_state.setText(str(state))


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


def clear_data_cache(self: NewMainWindow) -> None:
    """Clear the data cache.

    This clears all lists with sensor data.
    """
    self.time_data = []
    self.pressure_1_data = []
    self.pressure_2_data = []
    self.pressure_3_data = []
    self.pressure_4_data = []

    self.temperature_1_data = []
    self.temperature_2_data = []

    self.load_cell_1_data = []
    self.load_cell_2_data = []
    self.differential_pressure_data = []


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
            self.button_run_n20_purge_sequence.setEnabled(True)
            self.button_run_ignition_sequence.setEnabled(True)
            self.button_toggle_n2_purge_valve.setEnabled(True)
            self.button_toggle_n2_pressure_valve.setEnabled(True)
            self.button_toggle_n2o_main_valve.setEnabled(True)
            self.button_start_sequence.setEnabled(True)
        case False:
            self.button_run_n20_purge_sequence.setEnabled(False)
            self.button_run_ignition_sequence.setEnabled(False)
            self.button_toggle_n2_purge_valve.setEnabled(False)
            self.button_toggle_n2_pressure_valve.setEnabled(False)
            self.button_toggle_n2o_main_valve.setEnabled(False)
            self.button_start_sequence.setEnabled(False)


def reset_plots(self: NewMainWindow) -> None:
    """Reset the plots in the UI.

    This in useful when the sensors are calibrated to remove the old plots.
    """
    self.load_cell_nitrous_curve.clear()
    self.load_cell_thrust_curve.clear()
