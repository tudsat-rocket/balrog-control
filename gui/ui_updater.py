import queue
from control.definitions import State
from idlelib.sidebar import EndLineDelegator

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QDialogButtonBox

from control.definitions import EventType
from shared.shared_queues import n2o_main_valve_sensor_list, n2_purge_valve_sensor_list, n2o_vent_valve_sensor_list, n2o_fill_valve_sensor_list, n2_pressure_valve_sensor_list

def read_events_values_from_queue(self):
    """
    consume the newest values from the sensor queues
    """
    # get new pressure value from queue
    self.eventdata.append()


def update_ui(self):
    """
    Update the plots with new sensor values
    """

    try:
        # set waiting to false
        event = self.event_queue.get(False)
        print(f"received event {event}")
    except queue.Empty:
        # queue is empty, Nothing to do.
        return

    match event['type']:
        case EventType.CONNECTION_STATUS_UPDATE:
            update_connection_state(self, event)
        # case EventType.VALVE_STATUS_UPDATE:
        #     update_valve_state(self, event)
        case EventType.SEQUENCE_STARTED:
            update_sequence_state(self, False)
            clear_data_cache(self)
        case EventType.SEQUENCE_STOPPED:
            update_sequence_state(self, True)
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


def update_valve_states(self):
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

def update_connection_state(self, connection_event):
    """
    update the labels to display the current connection status
    """
    self.label_status_connection_state.setText(connection_event['status'])
    self.label_status_hostname_state.setText(connection_event['hostname'])
    self.label_status_port_state.setText(str(connection_event['port']))
    if connection_event['status'] == "Connected":
        self.button_connect.setText("Disconnect")
    elif connection_event['status'] == "Disconnected":
        self.button_connect.setText("Connect")

def update_sequence_state(self, enabled:bool):
    """
    enable and disable the buttons to start a sequence or do abort a sequence
    """
    # disable/enable start sequence button
    self.button_start_sequence.setEnabled(enabled)
    self.button_connect.setEnabled(enabled)

    self.button_selfcheck.setEnabled(enabled)
    self.button_test_horn.setEnabled(enabled)
    self.button_test_light.setEnabled(enabled)

    self.button_open_sequence.setEnabled(enabled)
    self.button_reload_sequence.setEnabled(enabled)

    self.button_abort_sequence.setEnabled(not enabled)

def update_valve_state(self, event):
    print(event)
    match event['valve']:
        case "main":
            self.label_valve_status_n20_main_state.setText(str(event['state']))
        case "vent":
            self.label_valve_status_n20_vent_state.setText(str(event['state']))
        case "fill":
            self.label_valve_status_n20_fill_state.setText(str(event['state']))

def show_info_event(self, info_event):
    """
    Show a dialog with an error message
    """
    # @TODO(Nucleus): redesign with pyside designer
    dlg = QDialog(self)
    dlg.setWindowTitle(info_event["title"])
    message = QLabel(info_event['message'])
    layout = QVBoxLayout()
    layout.addWidget(message)
    dlg.setLayout(layout)
    dlg.exec()

def show_confirmation_event(self, confirmation_event):
    """
    Show a dialog with an confirmation request
    """
    dlg = QDialog(self)
    dlg.setWindowTitle(confirmation_event["title"])
    message = QLabel(confirmation_event['message'])
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttonBox.accepted.connect(confirmation_event["confirm"])
    buttonBox.accepted.connect(dlg.accept)
    buttonBox.rejected.connect(confirmation_event["cancel"])
    buttonBox.rejected.connect(dlg.reject)
    layout = QVBoxLayout()
    layout.addWidget(message)
    layout.addWidget(buttonBox)
    dlg.setLayout(layout)
    dlg.exec()


def show_sequence_error(self, error_event):
    """
    Show a dialog with an error message
    """
    # @TODO(Nucleus): redesign with pyside designer
    dlg = QDialog(self)
    dlg.setWindowTitle("something went wrong")
    message = QLabel(error_event['message'])
    layout = QVBoxLayout()
    layout.addWidget(message)
    dlg.setLayout(layout)
    dlg.exec()

def clear_data_cache(self):
    """
    clear the data cache
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

def update_state(self, event):
    match event["new_state"]:
        case State.GREEN_STATE:
            self.group_state_green.setStyleSheet("background-color: rgb(143, 240, 164);")

            self.group_state_yellow.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.group_state_red.setStyleSheet("background-color: rgb(255, 255, 255);")
        case State.YELLOW_STATE:
            self.group_state_yellow.setStyleSheet("background-color: rgb(249, 240, 107);")

            self.group_state_green.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.group_state_red.setStyleSheet("background-color: rgb(255, 255, 255);")
        case State.RED_STATE:
            self.group_state_red.setStyleSheet("background-color: rgb(255, 160, 160);")

            self.group_state_yellow.setStyleSheet("background-color: rgb(255, 255, 255);")
            self.group_state_green.setStyleSheet("background-color: rgb(255, 255, 255);")

def update_arming_state(self, event):
    match event["new_state"]:
        case True:
            self.button_run_n20_purge_sequence.setEnabled(True)
            self.button_run_ignition_sequence.setEnabled(True)
            self.button_toggle_n2_purge_valve.setEnabled(True)
            self.button_toggle_n2_pressure_valve.setEnabled(True)
            self.button_toggle_n2o_fill_valve.setEnabled(True)
            self.button_start_sequence.setEnabled(True)
        case False:
            self.button_run_n20_purge_sequence.setEnabled(False)
            self.button_run_ignition_sequence.setEnabled(False)
            self.button_toggle_n2_purge_valve.setEnabled(False)
            self.button_toggle_n2_pressure_valve.setEnabled(False)
            self.button_toggle_n2o_fill_valve.setEnabled(False)
            self.button_start_sequence.setEnabled(False)