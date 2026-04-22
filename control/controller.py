import os
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep
from typing import Any

import interval_timer
import yaml

from shared.state import disk_queue
from control.data_handling import TelemetryLogger
from control.actor import Actor
from control.brick_handling import StackHandler
from control.definitions import ActionType, ActorType, EventType, State, SensorType
from control.sensor import Sensor
from control.test_definition_parsing import parse_csv
from control.sensor_callbacks import create_master_callback


class NotConnectedException(Exception):
    def __init__(self, event_queue, **kwargs):
        print("Not connected. Please connect to the test bench first!")
        event_queue.put(
            {
                "type": EventType.INFO_EVENT,
                "title": "Not connected",
                "message": "Please connect to the test bench first!",
            }
        )


class NotAllowedInThisState(Exception):
    def __init__(self, event_queue, **kwargs):
        print(
            "This action is not allowed in the current state. "
            "Please change the state first"
        )
        event_queue.put(
            {
                "type": EventType.INFO_EVENT,
                "title": "Not allowed",
                "message": "This action is not allowed in the current state. "
                "Please change the state first",
            }
        )


class Controller(Thread):
    sensor_enabled = False
    connected = False
    servo_fill_open = False
    servo_vent_open = False
    servo_main_open = False
    servo_pressurization_open = False
    servo_purge_open = False
    solenoid_quick_disconnect_open = False
    servo_quick_disconnect_open = False
    abort_sequence = False

    armingState: bool = False
    currentState: State = State.GREEN_STATE

    def __init__(
        self,
        event_queue: Queue,
        thread_killer,
        abort_signal,
        run_signal,
        connected_signal,
    ):
        super().__init__(target=None)
        self.t0_wall = time.time()
        self.t0_perf = time.perf_counter()
        self.actors = {}
        # @TODO(Nucleus): use correct type annotation "name": str, "sensor": Sensor
        self.sensors = {}
        self._construct_actors()
        self._construct_sensors()
        self.brick_stack = StackHandler()
        self.ignition_sequence = parse_csv(
            Path("config/operations/ignition_sequence.csv")
        )
        self.purge_sequence = parse_csv(
            Path("config/operations/purge_sequence.csv")
        )
        self.sequence = None
        self.event_queue: Queue = event_queue
        self.thread_killer = thread_killer
        self.abort_signal = abort_signal
        self.run_signal = run_signal
        self.connected_signal = connected_signal

        self.telemetry_logger = TelemetryLogger(f"telemetry_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}")

        # Thread starten, der die disk_queue aus shared/state abarbeitet
        self.logging_thread = Thread(
            target=self.telemetry_logger.run,
            args=(disk_queue, thread_killer),
            daemon=True
        )
        self.logging_thread.start()

        self.start()

    def run(self):
        self._thread_loop()

    def join(self, timeout=None):
        super().join()

    # ++++++++++++
    # Gui API
    # ++++++++++++

    def connect(self, host: str, port: int) -> bool:
        if self.connected:
            self.brick_stack.stop_connection()
            self.connected = False
            self.connected_signal.clear()
            self.event_queue.put(
                {
                    "type": EventType.CONNECTION_STATUS_UPDATE,
                    "status": "Disconnected",
                    "hostname": "unkown",
                    "port": "unkown",
                }
            )
            return False  # Explicitly return False when disconnecting
        else:
            print(f"Connect to {host}:{port}")
            try:
                # @TODO the UI freezes while waiting for a new connection.
                #  This could be solved with signals.
                self.brick_stack.start_connection(host, port)
                self.event_queue.put(
                    {
                        "type": EventType.CONNECTION_STATUS_UPDATE,
                        "status": "Connected",
                        "hostname": host,
                        "port": port,
                    }
                )
                # set config for all bricks
                self._set_configuration()
                self.connected = True
                self.connected_signal.set()
                # Turn all lights on after connecting
                try:
                    #self.reset_t0()
                    #uid = self.actors["light"].get_br_uid()
                    #self.actors["light"].action(
                    #    ActionType.LIGHT_ALL, self.brick_stack.get_device(uid)
                    #)
                    #self.read_valve_states()


                    self.enable_all_sensor_callbacks()
                    self.close_all_valves()
                except Exception as e:
                    print(f"Failed to set initial state: {e}")
                return True
            except Exception as e:
                print(f"Failed to connect to {host}:{port}: {e}")
                self.event_queue.put(
                    {
                        "type": EventType.CONNECTION_STATUS_UPDATE,
                        "status": "Connection failed",
                        "hostname": host,
                        "port": port,
                    }
                )
                self.connected = False
                self.connected_signal.clear()
                return False

    def adjust_valve_if_at_limit(self, valve: str, position: int) -> None:
        actor = self.actors[valve]
        adjust = 50
        brick = self.brick_stack.get_device(actor.get_br_uid())

        if position == actor.open_position and actor.open_position > actor.closed_position:
            brick.set_position(actor.output, actor.open_position - adjust)
        elif position == actor.open_position:
            brick.set_position(actor.output, actor.open_position + adjust)
        elif position == actor.closed_position and actor.open_position > actor.closed_position:
            brick.set_position(actor.output, actor.closed_position + adjust)
        elif position == actor.closed_position:
            brick.set_position(actor.output, actor.closed_position - adjust)

    def read_valve_states(self) -> None:
        sensor_names = [
            "main_valve_sensor",
            "fill_valve_sensor",
            "vent_valve_sensor",
            "purge_valve_sensor",
            "pressurization_valve_sensor",
        ]
        lists = [
            main_valve_sensor_list,
            fill_valve_sensor_list,
            vent_valve_sensor_list,
            purge_valve_sensor_list,
            pressurization_valve_sensor_list,
        ]
        # use strict=True to raise a ValueError if the
        # iterables are of non-uniform length.
        for sensor, sensor_list in zip(sensor_names, lists, strict=True):
            print("Reading " + sensor)
            sensor_list[0].append(datetime.now())
            sensor_list[1].append(
                self.brick_stack.get_device(
                    self.sensors[sensor].get_br_uid()
                ).get_current_position(self.sensors[sensor].channel)
            )

    def stack_state(self) -> dict[str, Any]:
        # Placeholder implementation to ensure a dictionary is always returned
        return {"state": "stack_state_placeholder"}

    def valve_state(self) -> dict[str, Any]:
        # Placeholder implementation to ensure a dictionary is always returned
        return {"state": "valve_state_placeholder"}

    def self_check(self) -> bool:
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        print("Performing self check...")
        self.event_queue.put({"type": EventType.INFO_EVENT, "status": "Self Check"})

        for actor in self.actors:
            rc = actor.check(self.brick_stack.get_device(actor.get_br_uid()))
            if not rc:
                self.event_queue.put(
                    {"type": EventType.INFO_EVENT, "status": "Self check failed"}
                )
                return False

        self.event_queue.put(
            {"type": EventType.INFO_EVENT, "status": "Self check passed"}
        )
        return True

    def check_solenoid_closed(self) -> bool:
        """Check if the solenoid is closed.

        Check if the solenoid is closed. Return True if the solenoid is closed,
        return False if the solenoid is open.
        """

        uid = self.actors["qd_solenoid"].get_br_uid()
        output = self.actors["qd_solenoid"].get_output()
        io_bricklet = self.brick_stack.get_device(uid)
        values = io_bricklet.get_value()
        return values[output] == 0

    def get_servo_position(self) -> list[bool]:
        """Returns a list with all server positions.

        If a servo is open, the entry is True,
        if the Servo has position 0, the value is False.
        """
        # We only need the ID of one valve, as all servos are
        # connected to the same servobricklet
        uid = self.actors["main_valve"].get_br_uid()
        servo_bricklet = self.brick_stack.get_device(uid)
        # each is list of length 10
        enabled, current_position, current_velocity, current, input_voltage = (
            servo_bricklet.get_status()
        )
        result = [False] * len(current_position)
        for i in range(len(current_position)):
            result[i] = (current_position[i] == 0)
        return result

    def check_all_servos_closed(self) -> bool:
        """Check if all servos are closed.

        Check if all servos are closed. Return True if all servo are closed,
        return False if at least one servo is open.
        """
        servo_state = self.get_servo_position()
        return all(servo_state)

    def request_go_to_green_state(self):
        """Request to to to the green state.

        This requires that all valves are closed and
        no bottle are connected anymore. There is no danger anymore
        To go into green state, we have to be in the yellow state before.
        It is not allowed to change from red to green directly.
        """
        if self.currentState != State.YELLOW_STATE and self.currentState != State.GREEN_STATE:
            self.event_queue.put(
                {
                    "type": EventType.CONFIRMATION_EVENT,
                    "title": "Confirm Procedure Override",
                    "message": f"Do you really want to go to GREEN state directly? "
                    f"Procedure demands transition is made "
                    f"only from YELLOW state."
                    f"\n (Current State: {self.currentState})",
                    "cancel": lambda: None,
                    "confirm": lambda: self.go_to_green_state(),
                }
            )
        else:
            self.go_to_green_state()

    def go_to_green_state(self):
        """Go to the green state.

        This requires that all valves are closed and
        no bottle are connected anymore. There is no danger anymore
        To go into green state, we have to be in the yellow state before.
        It is not allowed to change from red to green directly.
        """
        if self.armingState:
            self.toggle_arming()
        #self.set_light_to_green()
        self.currentState = State.GREEN_STATE
        self.event_queue.put(
            {"type": EventType.STATE_CHANGE, "new_state": State.GREEN_STATE}
        )

    def request_go_to_yellow_state(self):
        """Request to go into the yellow state.

        For this, all valves have to be closed. If not every valve is closed,
        this will trigger an alert dialog and will not set the light to yellow.
        """
        # check if all valves are closed and only enter his mode if this is true
        if not self.check_all_servos_closed() or not self.check_solenoid_closed():
            self.event_queue.put(
                {
                    "type": EventType.CONFIRMATION_EVENT,
                    "title": "Confirm Procedure Override",
                    "message": "WARNING: SOME VALVES ARE OPEN!!! "
                    "Do you really want to go to YELLOW state.",
                    "cancel": lambda: None,
                    "confirm": lambda: self.go_to_yellow_state(),
                }
            )
        else:
            self.go_to_yellow_state()

    def go_to_yellow_state(self):
        if self.armingState:
            self.toggle_arming()
        #self.set_light_to_yellow()
        self.currentState = State.YELLOW_STATE
        self.event_queue.put(
            {"type": EventType.STATE_CHANGE, "new_state": State.YELLOW_STATE}
        )

    def request_go_to_red_state(self):
        """Request: Go to red state.

        This enabled the dangerous operations. Might require confirmation.
        """
        print("Request to do to the red state")
        if self.currentState != State.YELLOW_STATE:
            print("request override")
            self.event_queue.put(
                {
                    "type": EventType.CONFIRMATION_EVENT,
                    "title": "Confirm Procedure Override",
                    "message": f"Do you really want to go to RED state directly?"
                    f" Procedure demands transition is made only from"
                    f" YELLOW state. \n (Current State: {self.currentState})",
                    "cancel": lambda: None,
                    "confirm": lambda: self.go_to_red_state(),
                }
            )
        else:
            self.go_to_red_state()

    def go_to_red_state(self):
        """Go to red state. This enabled the dangerous operations"""
        #self.set_light_to_red()
        self.currentState = State.RED_STATE
        self.event_queue.put(
            {"type": EventType.STATE_CHANGE, "new_state": State.RED_STATE}
        )

    def test_light(self) -> bool:
        """Toggles every light color for 1s and turns off all lights afterward"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        uid = self.actors["light"].get_br_uid()
        self.actors["light"].action(
            ActionType.LIGHT_ALL, self.brick_stack.get_device(uid)
        )
        self.actors["light"].action(
            ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid)
        )
        sleep(1)
        self.actors["light"].action(
            ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid)
        )
        sleep(1)
        self.actors["light"].action(
            ActionType.LIGHT_RED, self.brick_stack.get_device(uid)
        )
        sleep(1)
        self.actors["light"].action(
            ActionType.LIGHT_OFF, self.brick_stack.get_device(uid)
        )
        return True

    def set_light_to_red(self) -> None:
        """Sets the light to Red"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["light"].get_br_uid()
        self.actors["light"].action(
            ActionType.LIGHT_RED, self.brick_stack.get_device(uid)
        )

    def set_light_to_yellow(self):
        """Set the light to yellow"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["light"].get_br_uid()
        self.actors["light"].action(
            ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid)
        )

    def set_light_to_green(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["light"].get_br_uid()
        self.actors["light"].action(
            ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid)
        )

    def test_horn(self) -> bool:
        """Trigger the horn"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        uid = self.actors["horn"].get_br_uid()
        self.actors["horn"].action(
            ActionType.SOUND_HORN, self.brick_stack.get_device(uid)
        )
        return True

    def test_counter(self):
        """Resets and start the counter on the segment display"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["segment_display"].get_br_uid()
        self.actors["segment_display"].action(
            ActionType.COUNTER_RESET, self.brick_stack.get_device(uid)
        )
        self.actors["segment_display"].action(
            ActionType.COUNTER_START, self.brick_stack.get_device(uid)
        )
        return True

    #####
    #   Servo/Valve controller #
    #####

    def open_main_valve(self):
        uid = self.actors["main_valve"].get_br_uid()
        self.actors["main_valve"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_main_open = True

    def close_main_valve(self):
        uid = self.actors["main_valve"].get_br_uid()
        self.actors["main_valve"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_main_open = False

    def open_fill_valve(self):
        """This valve should be opened slow"""
        uid = self.actors["fill_valve"].get_br_uid()
        self.actors["fill_valve"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_fill_open = True

    def close_fill_valve(self):
        uid = self.actors["fill_valve"].get_br_uid()
        self.actors["fill_valve"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_fill_open = False

    def open_pressurization_valve(self):
        uid = self.actors["pressurization_valve"].get_br_uid()
        self.actors["pressurization_valve"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_pressurization_open = True

    def close_pressurization_valve(self):
        uid = self.actors["pressurization_valve"].get_br_uid()
        self.actors["pressurization_valve"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_pressurization_open = False

    def open_vent_valve(self):
        uid = self.actors["vent_valve"].get_br_uid()
        self.actors["vent_valve"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_vent_open = True

    def close_vent_valve(self):
        uid = self.actors["vent_valve"].get_br_uid()
        self.actors["vent_valve"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_vent_open = False

    def open_purge_valve(self):
        uid = self.actors["purge_valve"].get_br_uid()
        self.actors["purge_valve"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_purge_open = True

    def close_purge_valve(self):
        uid = self.actors["purge_valve"].get_br_uid()
        self.actors["purge_valve"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_purge_open = False

    def open_quick_disconnect_solenoid(self):
        uid = self.actors["qd_solenoid"].get_br_uid()
        self.actors["qd_solenoid"].action(
            ActionType.SOLENOID_OPEN, self.brick_stack.get_device(uid)
        )
        self.solenoid_quick_disconnect_open = True

    def close_quick_disconnect_solenoid(self):
        uid = self.actors["qd_solenoid"].get_br_uid()
        self.actors["qd_solenoid"].action(
            ActionType.SOLENOID_CLOSE, self.brick_stack.get_device(uid)
        )
        self.solenoid_quick_disconnect_open = False

    def open_quick_disconnect_servo(self):
        uid = self.actors["qd_servo"].get_br_uid()
        self.actors["qd_servo"].action(
            ActionType.SERVO_OPEN, self.brick_stack.get_device(uid)
        )
        self.servo_quick_disconnect_open = False

    def close_quick_disconnect_servo(self):
        uid = self.actors["qd_servo"].get_br_uid()
        self.actors["qd_servo"].action(
            ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid)
        )
        self.servo_quick_disconnect_open = False

    def toggle_main_valve(self):
        """Toggle the main valve from open to close"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_main_open:
            self.close_main_valve()
        else:
            self.open_main_valve()

        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "main",
                "state": self.servo_main_open,
            }
        )
        return True

    def toggle_vent_valve(self):
        """Toggle the vent between open to close"""
        print("toggle vent valve")
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_vent_open:
            self.close_vent_valve()
        else:
            self.open_vent_valve()
        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "vent",
                "state": self.servo_vent_open,
            }
        )

    def toggle_fill_valve(self):
        """Toggle the fill valve between open to close"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_fill_open:
            self.close_fill_valve()
        else:
            self.open_fill_valve()
        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "fill",
                "state": self.servo_fill_open,
            }
        )

    def toggle_purge_valve(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if (
            not self.currentState == State.RED_STATE or not self.armingState
        ):  # @TODO test
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_purge_open:
            self.close_purge_valve()
            self.servo_purge_open = False
        else:
            self.open_purge_valve()
            self.servo_purge_open = True

        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "purge",
                "state": self.servo_purge_open,
            }
        )

    def toggle_pressurization_valve(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_pressurization_open:
            self.close_pressurization_valve()
            self.servo_pressurization_open = False
        else:
            self.open_pressurization_valve()
            self.servo_pressurization_open = True
        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "pressurization",
                "state": self.servo_pressurization_open,
            }
        )

    def toggle_quick_disconnect_solenoid(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.solenoid_quick_disconnect_open:
            self.close_quick_disconnect_solenoid()
            self.solenoid_quick_disconnect_open = False
        else:
            self.open_quick_disconnect_solenoid()
            self.solenoid_quick_disconnect_open = True

        self.event_queue.put(
            {
                "type": EventType.VALVE_STATUS_UPDATE,  # @TODO
                "valve": "quick_disconnect",
                "state": self.solenoid_quick_disconnect_open,
            }
        )

    def trigger_quick_disconnect(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.solenoid_quick_disconnect_open or self.servo_fill_open:
            # the solenoid has to be closed to allow the servo to open
            raise NotAllowedInThisState(self.event_queue)

        self.open_quick_disconnect_servo()
        sleep(1.5)
        self.close_quick_disconnect_servo()


        self.event_queue.put(
            {
                # @TODO (Nucleus): this is a servo and not a valve
                "type": EventType.VALVE_STATUS_UPDATE,
                "valve": "quick_disconnect_servo",
                "state": self.servo_quick_disconnect_open,
            }
        )

    def close_all_valves(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        self.close_main_valve()
        self.close_pressurization_valve()
        self.close_fill_valve()
        self.close_purge_valve()
        self.close_vent_valve()
        self.close_quick_disconnect_servo()
        self.close_quick_disconnect_solenoid()

    def run_purge_sequence(self):
        """Run the purge sequence
        only allowed in rea state
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.purge_sequence is not None:
            self.sequence = self.purge_sequence
            self.run_signal.set()

    def request_run_ignition_sequence(self):
        """Run the ignition sequence
        this is a dangerous operation and is only allowed in red state
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)
        if self.ignition_sequence is not None:
            self.event_queue.put(
                {
                    "type": EventType.CONFIRMATION_EVENT,
                    "title": "Confirm Ignition",
                    "message": f"                      DANGER!                    \n"
                               f"Do you really want to IGNITE?       \n"
                               f"                      DANGER!                      ",
                    "cancel": lambda: None,
                    "confirm": lambda: self.run_ignition_sequence(),
                }
            )

    def run_ignition_sequence(self):
            self.sequence = self.ignition_sequence
            self.run_signal.set()


    def load_test_definition(self, path: os.PathLike) -> bool:
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if path is not None:
            self.sequence = parse_csv(path)
            return True
        else:
            print(f"Error {path} is not a valid path")
            return False

    def calibrate_thrust_load(self, input_weight: str, clear_callback) -> None:
        """Calibrates the thrust load cell with the given weight"""
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        try:
            calibration_weight = int(float(input_weight) * 1000)
            uid = self.sensors["load_cell_thrust"].get_br_uid()
            self.sensors["load_cell_thrust"].calibrate_load(
                self.brick_stack.get_device(uid), calibration_weight
            )
            # Reset existing sensor data before calibration
            # (keep 2-list structure so GUI clears plot)
            load_cell_thrust_sensor_list[:] = [[], []]
            self.event_queue.put(
                {
                    "type": EventType.RESET_PLOTS,
                }
            )
            clear_callback()
        except Exception:
            self.event_queue.put(
                {
                    "type": EventType.INFO_EVENT,
                    "title": "Invalid calibration value",
                    "message": f'The given value of "{input_weight}" is invalid.',
                }
            )

    def calibrate_ox_load(self, input_weight: str, clear_callback) -> None:
        """Calibrates the nitrous load cell with the given weight.

        @TODO(Nucleus): We could merge both calibrate methods together.
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        try:
            calibration_weight = int(float((input_weight or "").strip()) * 1000)
            uid = self.sensors["Ox load cell"].get_br_uid()
            self.sensors["Ox load cell"].calibrate_load(
                self.brick_stack.get_device(uid), calibration_weight
            )
            # Reset existing sensor data before calibration
            # (keep 2-list structure so GUI clears plot)
            load_cell_ox_sensor_list[:] = [[], []]
            self.event_queue.put(
                {
                    "type": EventType.RESET_PLOTS,
                }
            )
            clear_callback()
        except Exception:
            self.event_queue.put(
                {
                    "type": EventType.INFO_EVENT,
                    "title": "Invalid calibration value",
                    "message": f'The given value of "{input_weight}" is invalid.',
                }
            )

    def toggle_arming(self):
        """Toggle the arming state. Only if arming is true, we can trigger the
        purge valve, the fill valve, the pressure valve and the igniter
        """
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)
        if self.armingState:
            self.armingState = False
        else:
            self.armingState = True

        self.event_queue.put(
            {
                "type": EventType.ARMING_STATE_CHANGE,
                "new_state": self.armingState,
            }
        )

    def verify_sequence(self) -> bool:
        if self.sequence is None:
            self.event_queue.put(
                {"type": EventType.SEQUENCE_ERROR, "message": "No sequence loaded."}
            )
            return False

        for step in self.sequence:
            if step[0] not in self.actors:
                self.event_queue.put(
                    {
                        "type": EventType.SEQUENCE_ERROR,
                        "message": f"Actor {step[0]} not found.",
                    }
                )
                return False

        return True

    def enable_all_sensor_callbacks(self):
        """Enable the callbacks and start the sensor reading"""
        print("enable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            try:
                sensor.enable_callback(self.brick_stack.get_device(uid))
            except Exception as e:
                print(f"could not enable sensor {sensor.get_br_uid()}", e)

    def disable_all_sensor_callbacks(self):
        """Disable all callbacks. No new sensor values will be added"""
        print("disable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            sensor.disable_callback(self.brick_stack.get_device(uid))

    def toggle_sensors(self):
        """Toggles the sensor callbacks on and off.

        This starts  and stops the data recording / plotting.
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        if not self.sensor_enabled:
            print("enabled all sensors")
            self.enable_all_sensor_callbacks()
            self.sensor_enabled = True
        else:
            print("disabled all sensors")
            self.disable_all_sensor_callbacks()
            self.sensor_enabled = False

    def stop(self):
        self.logging_thread.join(timeout=2)

    def start_sequence(self) -> bool:
        """Start the loaded sequence."""
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        print("Start sequence...")
        if self.sequence is not None:
            self.event_queue.put({"type": EventType.SEQUENCE_STARTED})

            # --- run sequence ---
            print("running sequence")
            self.run_signal.set()
            return True

        else:
            self.event_queue.put(
                {
                    "type": EventType.SEQUENCE_ERROR,
                    "message": "No Sequence found. Please load a sequence first",
                }
            )
            return False

    def end_sequence(self) -> bool:
        # --- Finish sequence
        # wait a moment to ensure every callback is done
        # print("waiting for callbacks to complete...")
        # sleep(0.5)
        # dump_sensor_to_file() no needed anymore
        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
        return True

    def abort(self) -> None:
        """Abort the sequence.

        This aborts the currently running sequence.
        An abort is only possible if we are in the red-state.
        This was requested by Tyler due to priority
        of security of personnel at test site.
        """
        # Abort only in RED_STATE
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        # stop the sequence worker
        self.abort_signal.set()

        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})

        # Close All Valves
        self.actors["main_valve"].action(
            ActionType.SERVO_CLOSE,
            self.brick_stack.get_device(self.actors["main_valve"].get_br_uid()),
        )
        self.actors["vent_valve"].action(
            ActionType.SERVO_CLOSE,
            self.brick_stack.get_device(self.actors["vent_valve"].get_br_uid()),
        )
        self.actors["fill_valve"].action(
            ActionType.SERVO_CLOSE,
            self.brick_stack.get_device(self.actors["fill_valve"].get_br_uid()),
        )

        # Open Purge Valve
        self.actors["purge_valve"].action(
            ActionType.SERVO_OPEN,
            self.brick_stack.get_device(self.actors["purge_valve"].get_br_uid()),
        )

        # visual and auditory warnings
        # @TODO do we want to tigger the horn here?
        #self.actors["horn"].action(
        #    ActionType.SOUND_HORN,
        #    self.brick_stack.get_device(self.actors["horn"].get_br_uid()),
        #)

    # ++++++
    # Internal methods
    # ++++++

    def _set_configuration(self):
        # we have to wait until the brick are there @TODO find out why
        sleep(0.5)
        for actor in self.actors.values():
            brick = self.brick_stack.get_device(actor.get_br_uid())

            match actor.type:
                case ActorType.TRIGGER:
                    brick.set_configuration(actor.output, "o", False)
                case ActorType.LIGHT:
                    brick.set_configuration(actor.output, "o", False)
                    brick.set_configuration(actor.output + 1, "o", False)
                    brick.set_configuration(actor.output + 2, "o", False)
                case ActorType.HORN:
                    brick.set_configuration(actor.output, "o", False)
                case ActorType.SERVO:
                    # with 0 is the position instantly set
                    velocity = 0
                    acceleration = 0
                    deceleration = 0
                    pwm_min = 500  # pwm values from datasheet
                    pwm_max = 2500
                    brick.set_pulse_width(actor.output, pwm_min, pwm_max)
                    brick.set_motion_configuration(
                        actor.output, velocity, acceleration, deceleration
                    )
                case ActorType.SOLENOID:
                    brick.set_configuration(actor.output, "o", False)

        for sensor in self.sensors.values():
            brick = self.brick_stack.get_device(sensor.get_br_uid())

            match sensor.type:
                case SensorType.PRESSURE:
                    #pass
                    # TODO Config
                    brick.set_sample_rate(2)
                    brick.set_gain(0)
                    #brick.set_sample_rate(0)

    def _construct_actors(self) -> None:
        """Construct all actors from the balrog.yaml"""
        with open("config/balrog.yaml") as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config["actors"]

            for actor in actors:
                # Convert actor type to ActorType enum
                # actor_type = ActorType[actor['type'].upper()]
                self.actors[actor["name"]] = Actor(
                    actor["name"],
                    actor["type"],
                    actor["uid"],
                    actor["output"],
                    actor.get("closed_position", -1),
                    actor.get("open_position", -1),
                )

        print(self.actors)

    def _construct_sensors(self) -> None:
        with open("config/balrog.yaml") as f:
            sensors_config = yaml.load(f, Loader=yaml.SafeLoader)["sensors"]

        from collections import defaultdict
        by_uid = defaultdict(list)
        for cfg in sensors_config:
            by_uid[cfg["uid"]].append(cfg)

        for actor_name, actor_obj in self.actors.items():
            if actor_obj.type == ActorType.SERVO:
                by_uid[actor_obj.get_br_uid()].append({
                    'name': actor_name,
                    'channel': actor_obj.output,
                    'type': SensorType.SERVO_STATE,
                    'period': -1
                })

        for uid, cfgs in by_uid.items():
            # Master-Dispatcher für alle Kanäle dieser UID
            units = [{'name': c["name"], 'channel': c["channel"]} for c in cfgs]
            master_cb = create_master_callback(self, units)

            for cfg in cfgs:
                self.sensors[cfg["name"]] = Sensor(
                    cfg["name"], cfg["type"], uid, cfg["channel"],
                    master_cb,  # Geteilter Dispatcher
                    cfg["period"]
                )

        print(f"Initialized {len(self.sensors)} sensors.")

    # ++++++
    # Thread target
    # ++++++
    def _sequence_worker(self):
        if self.sequence is None:
            self.event_queue.put(
                {"type": EventType.SEQUENCE_ERROR, "message": "No sequence to execute."}
            )
            return

        seq_local = self.sequence.copy()
        seq_idx = 0
        seq_ts = 0
        seq_len = len(seq_local)

        for _ in interval_timer.IntervalTimer(0.02):
            # signal used to abort the sequence with a button
            if self.abort_signal.is_set():
                self.abort_signal.clear()
                return

            while seq_idx < seq_len and int(seq_local[seq_idx][1]) <= seq_ts:
                tpl = seq_local[seq_idx]
                print(f"Executing: {tpl[0]} at TS: {tpl[1]} (Internal Clock: {seq_ts})")
                self.actors[tpl[0]].action(
                    tpl[2],
                    self.brick_stack.get_device(self.actors[tpl[0]].get_br_uid()),
                )
                seq_idx += 1

            if seq_idx >= seq_len:
                self.end_sequence()
                return

            seq_ts += 20

    def _thread_loop(self):
        while not self.thread_killer.is_set():
            # TODO Start durch self.run_signal.wait(timeout=1.0) ersetzen? Testn
            if self.run_signal.is_set():
                self.run_signal.clear()
                self._sequence_worker()

            sleep(0.1)
