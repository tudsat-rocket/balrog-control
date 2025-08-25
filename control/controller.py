import os
from datetime import datetime
from time import sleep

import yaml
import interval_timer

from threading import Thread
from typing import Any
from control.brick_handling import StackHandler
from control.definitions import ActionType, EventType, ActorType, State
from control.test_definition_parsing import parse_csv
from control.actor import Actor
from control.sensor import Sensor
from queue import Queue
from control.dump_sensor_to_file import dump_sensor_to_file

from shared.shared_queues import *

def current_to_pressure(current):
    """
    apply linear translation of current to pressure
    """
    # 100 = m*20.006 - m*4.001 =
    # 6.248047485
    # 0 = 6.248047485*4.001 => 24.992191
    # => f(x) = 6.248047485*current-24.992191
    # @todo verify calculation
    return 6.248047485*(current/1000000.0)-24.992191

def temperature_nitrous_callback(temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    #temperature_nitrous_sensor_queue.put(temperature)
    temperature_nitrous_sensor_list[0].append(datetime.now())
    #temperature_nitrous_sensor_list[0].append(1)
    temperature_nitrous_sensor_list[1].append(temperature)

def temperature_engine_callback(temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    #temperature_engine_sensor_queue.put(temperature)
    temperature_engine_sensor_list[0].append(datetime.now())
    #temperature_engine_sensor_list[0].append(1)
    temperature_engine_sensor_list[1].append(temperature)

def pressure_0_1_callback(channel, current):
    #print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    #print("----")
    #pressure_1_sensor_queue.put(current)
    if channel == 0:

        pressure_0_sensor_list[0].append(datetime.now())
        #pressure_0_sensor_list[0].append(1)
        pressure_0_sensor_list[1].append(current_to_pressure(current))
    elif channel == 1:
        pressure_1_sensor_list[0].append(datetime.now())
        #pressure_1_sensor_list[0].append(1)
        pressure_1_sensor_list[1].append(current_to_pressure(current))


def pressure_2_3_callback(channel, current):
    #print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    #pressure_3_sensor_queue.put(current)
    if channel == 0:
        differential_pressure_list[0].append(datetime.now())
        #differential_pressure_list[0].append(1)
        differential_pressure_list[1].append(current_to_pressure(current))
    elif channel == 1:
        pressure_2_sensor_list[0].append(datetime.now())
        #pressure_2_sensor_list[0].append(1)
        pressure_2_sensor_list[1].append(current_to_pressure(current))

def thrust_load_cell_callback(weight):
    #print("Weight thrust: " + str(weight) + " g")
    #load_cell_1_sensor_queue.put(weight)
    load_cell_1_sensor_list[0].append(datetime.now())
    #load_cell_1_sensor_list[0].append(1)
    load_cell_1_sensor_list[1].append(weight)

def nitrous_load_cell_callback(weight):
    #print("Weight nitrous: " + str(weight) + " g")
    #load_cell_2_sensor_queue.put(weight)
    load_cell_2_sensor_list[0].append(datetime.now())
    #load_cell_2_sensor_list[0].append(1)
    load_cell_2_sensor_list[1].append(weight)

def valve_sensor_callback(channel, position):
    match channel:
        case 0:
            n2o_fill_valve_sensor_list[0].append(datetime.now())
            n2o_fill_valve_sensor_list[1].append(position)
        case 1:
            n2o_vent_valve_sensor_list[0].append(datetime.now())
            n2o_vent_valve_sensor_list[1].append(position)
        case 2:
            n2o_main_valve_sensor_list[0].append(datetime.now())
            n2o_main_valve_sensor_list[1].append(position)
        case 3:
            n2_pressure_valve_sensor_list[0].append(datetime.now())
            n2_pressure_valve_sensor_list[1].append(position)
        case 4:
            n2_purge_valve_sensor_list[0].append(datetime.now())
            n2_purge_valve_sensor_list[1].append(position)

def differential_pressure_callback( channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    #differential_pressure_queue.put(current)
    differential_pressure_list[0].append(datetime.now())
    #differential_pressure_list[0].append(1)
    differential_pressure_list[1].append(current)

class NotConnectedException(Exception):
    def __init__(self, event_queue, **kwargs):
        print("Not connected. Please connect to the test bench first!")
        event_queue.put({"type": EventType.INFO_EVENT,
                              "title": "Not connected",
                              "message": "Please connect to the test bench first!",
                        }
                    )

class NotAllowedInThisState(Exception):
    def __init__(self, event_queue, **kwargs):
        print("This action is not allowed in the current state. Please change the state first")
        event_queue.put({"type": EventType.INFO_EVENT,
                              "title": "Not allowed",
                              "message": "This action is not allowed in the current state. Please change the state first",
                        }
                    )

class Controller(Thread):
    sensor_enabled = False
    connected = False
    servo_nitrous_fill_open = False
    servo_vent_open = False
    servo_main_open = False
    servo_pressure_open = False
    servo_purge_open = False
    servo_quick_disconnect_open = False
    abort_sequence = False

    armingState:bool = False
    currentState:State = State.GREEN_STATE


    def __init__(self, event_queue: Queue, thread_killer):
        Thread.__init__(self, target=self._sequence_worker, args=(self,))
        self.actors = {}
        self.sensors = {}
        self._construct_actors()
        self._construct_sensor()
        self.brick_stack = StackHandler()
        self.ignition_sequence = parse_csv("config/operations/ignition_sequence.csv")
        self.n2o_purge_sequence = parse_csv("config/operations/n20_purge_sequence.csv")
        self.sequence = None
        self.event_queue = event_queue
        self.thread_killer = thread_killer


    def run(self):
        super().run()

    def join(self, timeout = None):
        super().join()


    # ++++++++++++
    # Gui API
    # ++++++++++++

    def connect(self, host: str, port: int) -> bool:
        if self.connected:
            self.brick_stack.stop_connection()
            self.connected = False
            self.event_queue.put({"type": EventType.CONNECTION_STATUS_UPDATE,
                                  "status": "Disconnected",
                                  "hostname": "unkown",
                                  "port": "unkown"}
                                 )
        else:
            print(f"Connect to {host}:{port}")
            try:
                # @TODO the UI freezes while waiting for a new connection, could be solved with signals.
                self.brick_stack.start_connection(host, port)
                self.event_queue.put({"type": EventType.CONNECTION_STATUS_UPDATE,
                                      "status": "Connected",
                                      "hostname": host,
                                      "port": port}
                                     )
                # set config for all bricks
                self._set_configuration()
                # Turn all lights on after connecting
                try:
                    uid = self.actors["Light"].get_br_uid()
                    self.actors["Light"].action(ActionType.LIGHT_ALL, self.brick_stack.get_device(uid))
                except Exception as e:
                    print(f"Failed to turn on all lights: {e}")
                self.connected = True
                return True
            except Exception as e:
                print(f"Failed to connect to {host}:{port}: {e}")
                self.event_queue.put({"type": EventType.CONNECTION_STATUS_UPDATE,
                                      "status": "Connection failed",
                                      "hostname": host,
                                      "port": port}
                                     )
                return False



    def stack_state(self) -> dict[str, Any]:
        pass

    def valve_state(self) -> dict[str, Any]:
        pass

    def self_check(self) -> bool:
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        print("Performing self check...")
        self.event_queue.put({"type": EventType.INFO_EVENT,
                              "status": "Self Check"}
                             )

        for actor in self.actors:
            rc = actor.check(self.brick_stack.get_device(actor.get_br_uid()))
            if not rc:
                self.event_queue.put({"type": EventType.INFO_EVENT,
                                      "status": "Self check failed"})
                return False

        self.event_queue.put({"type": EventType.INFO_EVENT,
                              "status": "Self check passed"})
        return True

    def get_servo_position(self):
        """
        Returns a list with all servo. If a servo is open, the entry is True, if the Servo has position 0, the valve is False
        """
        uid = self.actors["N20MainValve"].get_br_uid()
        servo_bricklet =  self.brick_stack.get_device(uid)
        # each is list of length 10
        enabled, current_position, current_velocity, current, input_voltage = servo_bricklet.get_status()
        result = []
        for i in range(len(current_position)):
            result[i] = current_position[i] == 0
        return result

    def check_all_servos_closed(self):
        """
        check if all servos are closed. Return True if all servo are closed, return False if at least one servo is open
        """
        servo_state = self.get_servo_position()
        for i in servo_state:
            if i:
                return False
        # every servo is closed
        return True

    def request_go_to_green_state(self):
        """
        This requires that all valves are closed and no bottle are connected anymore. There is no danger anymore
        To go into green state, we have to be in the yellow state before. We can not chnage from red to green
        """
        if not self.currentState == State.YELLOW_STATE:
            self.event_queue.put({"type": EventType.CONFIRMATION_EVENT,
                                  "title": "Confirm Procedure Override",
                                  "message": f"Do you really want to go to GREEN state directly? Procedure demands transition is made only from YELLOW state.\n (Current State: {self.currentState})",
                                  "cancel": lambda: None,
                                  "confirm": lambda: self.go_to_green_state()}
                                 )
        else:
            self.go_to_green_state()
        
    def go_to_green_state(self):
        """
        This requires that all valves are closed and no bottle are connected anymore. There is no danger anymore
        To go into green state, we have to be in the yellow state before. We can not chnage from red to green
        """
        self.set_light_to_green()
        self.currentState = State.GREEN_STATE
        self.event_queue.put({"type": EventType.STATE_CHANGE,
                              "new_state": State.GREEN_STATE
                              }
                             )

    def request_go_to_yellow_state(self):
        """
        For this, all valves have to be closed. If not every valve is closed, this will trigger an alert dialog and
        will not set the light to yellow
        """
        # check if all valves are closed and only enter his mode if this is true

        if not self.check_all_servos_closed:
            self.event_queue.put({"type": EventType.CONFIRMATION_EVENT,
                                  "title": "Confirm Procedure Override",
                                  "message": "WARNING: SOME VALVES ARE OPEN!!! Do you really want to go to YELLOW state.",
                                  "cancel": lambda: None,
                                  "confirm": lambda: self.go_to_yellow_state()}
                                 )
        else: 
            self.go_to_yellow_state()

    def go_to_yellow_state(self):
        self.set_light_to_yellow()
        self.currentState = State.YELLOW_STATE
        self.event_queue.put({"type": EventType.STATE_CHANGE,
                                "new_state": State.YELLOW_STATE
                                }
                                )

    def request_go_to_red_state(self):
        """
        Requsest: Go to red state. This enabled the dangerous operations. Might require confirmation
        """
        if not self.currentState == State.YELLOW_STATE:
            self.event_queue.put({"type": EventType.CONFIRMATION_EVENT,
                                  "title": "Confirm Procedure Override",
                                  "message": f"Do you really want to go to RED state directly? Procedure demands transition is made only from YELLOW state. \n (Current State: {self.currentState})",
                                  "cancel": lambda: None,
                                  "confirm": lambda: self.go_to_red_state()}
                                 )
        else:
            self.go_to_red_state()

    def go_to_red_state(self):
        """
        Go to red state. This enabled the dangerous operations
        """
        self.set_light_to_red()
        self.currentState = State.RED_STATE
        self.event_queue.put({"type": EventType.STATE_CHANGE,
                                "new_state": State.RED_STATE
                                }
                                )

    def test_light(self) -> bool:
        """
        toggles every light color for 1s and turns off all lights afterward
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_ALL, self.brick_stack.get_device(uid))
        self.actors["Light"].action(ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_OFF, self.brick_stack.get_device(uid))
        return True

    def set_light_to_red(self) -> None:
        """
        Sets the light to Red
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(uid))

    def set_light_to_yellow(self):
        """
        Set the light to yellow
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid))

    def set_light_to_green(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid))

    def test_horn(self) -> bool:
        """
        trigger the horn
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        uid = self.actors["Horn"].get_br_uid()
        self.actors["Horn"].action(ActionType.SOUND_HORN, self.brick_stack.get_device(uid))
        return True

    def test_counter(self):
        """
        resets and start the counter on the segment display
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        uid = self.actors["SegmentDisplay"].get_br_uid()
        self.actors["SegmentDisplay"].action(ActionType.COUNTER_RESET, self.brick_stack.get_device(uid))
        self.actors["SegmentDisplay"].action(ActionType.COUNTER_START, self.brick_stack.get_device(uid))
        return True

    #####
    #   Servo/Valve controller #
    #####

    def open_n2o_main_valve(self):
        uid = self.actors["N20MainValve"].get_br_uid()
        self.actors["N20MainValve"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
        self.servo_main_open = True

    def close_n2o_main_valve(self):
        uid = self.actors["N20MainValve"].get_br_uid()
        self.actors["N20MainValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_main_open = False

    def open_n2o_fill_valve(self):
        """
        This valve should be opened slow
        """
        uid = self.actors["N20FillValve"].get_br_uid()
        self.actors["N20FillValve"].action(ActionType.SERVO_OPEN_SLOW, self.brick_stack.get_device(uid))
        self.servo_nitrous_fill_open = True

    def close_n2o_fill_valve(self):
        uid = self.actors["N20FillValve"].get_br_uid()
        self.actors["N20FillValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_nitrous_fill_open = False

    def open_n2_pressure_valve(self):
        uid = self.actors["N2PressureValve"].get_br_uid()
        self.actors["N2PressureValve"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
        self.servo_pressure_open = True

    def close_n2_pressure_valve(self):
        uid = self.actors["N2PressureValve"].get_br_uid()
        self.actors["N2PressureValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_pressure_open = False

    def open_n2o_vent_valve(self):
        uid = self.actors["N20VentValve"].get_br_uid()
        self.actors["N20VentValve"].action(ActionType.SERVO_OPEN_QUARTER_SLOW, self.brick_stack.get_device(uid))
        self.servo_vent_open = True

    def close_n2o_vent_valve(self):
        uid = self.actors["N20VentValve"].get_br_uid()
        self.actors["N20VentValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_vent_open = False

    def open_n2_purge_valve(self):
        uid = self.actors["N2PurgeValve"].get_br_uid()
        self.actors["N2PurgeValve"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
        self.servo_purge_open = True

    def close_n2_purge_valve(self):
        uid = self.actors["N2PurgeValve"].get_br_uid()
        self.actors["N2PurgeValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_purge_open = True

    def open_quick_disconnect(self):
        uid = self.actors["QuickDisconnect"].get_br_uid()
        self.actors["QuickDisconnect"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
        self.servo_quick_disconnect_open = True

    def close_quick_disconnect(self):
        uid = self.actors["QuickDisconnect"].get_br_uid()
        self.actors["QuickDisconnect"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
        self.servo_quick_disconnect_open = False

    def toggle_n2o_main_valve(self):
        """
        toggle the main valve from open to close
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_main_open:
            self.close_n2o_main_valve()
        else:
            self.open_n2o_main_valve()

        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "main",
                              "state": self.servo_main_open,
                                }
                             )
        return True

    def toggle_n2o_vent_valve(self):
        """
        toggle the vent between open to close
        """
        print("toggle vent valve")
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_vent_open:
            self.close_n2o_vent_valve()
        else:
            self.open_n2o_vent_valve()
        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "vent",
                              "state": self.servo_vent_open,
                              })

    def toggle_n2o_fill_valve(self):
        """
        toggle the fill valve between open to close
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_nitrous_fill_open:
            self.close_n2o_fill_valve()
        else:
            self.open_n2o_fill_valve()
        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "fill",
                              "state": self.servo_nitrous_fill_open,
                              })

    def toggle_n2_purge_valve(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE or not self.armingState: #@TODO test
            raise NotAllowedInThisState(self.event_queue)


        if self.servo_purge_open:
            self.close_n2_purge_valve()
            self.servo_purge_open = False
        else:
            self.open_n2_purge_valve()
            self.servo_purge_open = True

        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "purge",
                              "state": self.servo_purge_open,
                              })

    def toggle_n2_pressure_valve(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_pressure_open:
            self.close_n2_pressure_valve()
            self.servo_pressure_open = False
        else:
            self.open_n2_pressure_valve()
            self.servo_pressure_open = True
        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "pressure",
                              "state": self.servo_pressure_open,
                              })

    def toggle_quick_disconnect(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.servo_quick_disconnect_open:
            self.open_quick_disconnect()
            self.servo_quick_disconnect_open = False
        else:
            self.close_quick_disconnect()
            self.servo_quick_disconnect_open = True

        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "quick_disconnect",
                              "state": self.servo_quick_disconnect_open,
                              })

    def close_all_valves(self):
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        self.close_n2o_main_valve()
        self.close_n2_pressure_valve()
        self.close_n2o_fill_valve()
        self.close_n2_purge_valve()
        self.close_n2o_vent_valve()
        self.close_quick_disconnect()


    def run_n2o_purge_sequence(self):
        """
        run the purge sequence
        only allowed in rea state
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        if self.n2o_purge_sequence is not None:
            self.sequence = self.n2o_purge_sequence
            self.run()

    def run_ignition_sequence(self):
        """
        run the ignition sequence
        this is a dangerous operation and is only allowed in red state
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)
        if self.ignition_sequence is not None:
            self.sequence = self.ignition_sequence
            self.run()

    def load_test_definition(self, path: os.path) -> bool:
        if not self.connected:
            raise NotConnectedException(self.event_queue)
        if path is not None:
            self.sequence = parse_csv(path)
            return True
        else:
            print(f"Error {path} is not a valid path")
            return False

    def calibrate_thrust_load(self, weight):
        """
        calibrates the thrust load cell with the given weight
        depended on the given weight the following methods are called:
        weight: "": we use 0
        weight: "-1" use the tare function of the load cell
        weight: >0 use the given weight
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        # Clear existing sensor data before calibration
        load_cell_1_sensor_list.clear()

        if weight != "":
            weight = int(weight)
        elif weight == "-1":
            weight = None
        else:
            weight = 0

        uid = self.sensors["Thrust load cell"].get_br_uid()
        return self.sensors["Thrust load cell"].calibrate_load(self.brick_stack.get_device(uid), weight)

    def calibrate_nitrous_load(self, weight):
        """
        calibrates the nitrous load cell with the given weight
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        # Clear existing sensor data before calibration
        load_cell_2_sensor_list.clear()

        if weight != "":
            weight = int(weight)
        elif weight == "-1":
            weight = None
        else:
            weight = 0

        uid = self.sensors["Nitrous load cell"].get_br_uid()
        return self.sensors["Nitrous load cell"].calibrate_load(self.brick_stack.get_device(uid), weight)

    def toggle_arming(self):
        """
        Toggle the arming state. Only if arming is true, we can trigger the
         purge valve, the fill valve, the pressure valve and the igniter
        """
        if self.armingState:
            self.armingState = False
        else:
            self.armingState = True

        self.event_queue.put({"type": EventType.ARMING_STATE_CHANGE,
                              "new_state": self.armingState,
                              })


    def verify_sequence(self) -> bool:
        if self.sequence is None:
            self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": "No sequence loaded."})
            return False

        for step in self.sequence:
            if step[0] not in self.actors.keys():
                self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": f"Actor {step[0]} not found."})
                return False

        return True

    def enable_all_sensor_callbacks(self):
        """
        Enable the callbacks and start the sensor reading
        """
        print("enable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            sensor.enable_callback(self.brick_stack.get_device(uid))

    def disable_all_sensor_callbacks(self):
        """
        Disable all callbacks. No new sensor values will be added
        """
        print("disable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            sensor.disable_callback(self.brick_stack.get_device(uid))

    def toggle_sensors(self):
        """
        Toggles the sensor callbacks on and off. This starts  and stops the data recording / plotting
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        if not self.sensor_enabled:
            print("enable all sensors")
            self.enable_all_sensor_callbacks()
            self.sensor_enabled = True
        else:
            print("disable all sensors")
            self.disable_all_sensor_callbacks()
            self.sensor_enabled = False

    def dump_sensors_to_file(self):
        """
        wrapper for the dumping method from import
        """
        dump_sensor_to_file()

    def reset_sensors(self):
        # Disable all sensor callbacks before clearing the lists
        self.disable_all_sensor_callbacks()

        pressure_0_sensor_list.clear()
        pressure_1_sensor_list.clear()
        pressure_2_sensor_list.clear()
        pressure_3_sensor_list.clear()
        differential_pressure_list.clear()

        # temp
        temperature_nitrous_sensor_list.clear()
        temperature_engine_sensor_list.clear()

        # load cell
        load_cell_1_sensor_list.clear()
        load_cell_2_sensor_list.clear()

    def start_sequence(self) -> bool:
        """
        start the loaded sequence.
        """
        if not self.connected:
            raise NotConnectedException(self.event_queue)

        print("Start sequence...")
        if self.sequence is not None:
            self.event_queue.put({"type": EventType.SEQUENCE_STARTED})

            # --- run sequence ---
            print("running sequence")
            # start the sequence
            self.enable_all_sensor_callbacks()
            self.run()
            return True

        else:
            self.event_queue.put(
                {"type": EventType.SEQUENCE_ERROR, "message": "No Sequence found. Please load a sequence first"})
            return False


    def end_sequence(self) -> bool:

        self.disable_all_sensor_callbacks()

        # --- Finish sequence
        # wait a moment to ensure every callback is done
        # print("waiting for callbacks to complete...")
        sleep(0.5)
        dump_sensor_to_file()
        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
        return True


    def abort(self) -> None:
        """
        abort the sequence
        """
        # Requested by Tyler: Abort only in RED_STATE due to priority of security of personnel at test site.
        if not self.currentState == State.RED_STATE:
            raise NotAllowedInThisState(self.event_queue)

        # stop the sequence worker
        self.thread_killer.set()

        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})

        # Close All Valves
        self.actors["N20MainValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["N20MainValve"].get_br_uid()))
        self.actors["N20VentValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["N20VentValve"].get_br_uid()))
        self.actors["N20FillValve"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["N20FillValve"].get_br_uid()))

        # Open Purge Valve
        self.actors["N2PurgeValve"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(self.actors["N2PurgeValve"].get_br_uid()))

        # visual and auditory warnings
        # @TODO do we want to tigger the horn here?
        self.actors["Horn"].action(ActionType.SOUND_HORN, self.brick_stack.get_device(self.actors["Horn"].get_br_uid()))
        #self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(self.actors["Light"].get_br_uid()))

        self.disable_all_sensor_callbacks()

    def read_pressure_1(self):
        uid = self.sensors["Pressure 1"].get_br_uid()
        return self.sensors["Pressure 1"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_2(self):
        uid = self.sensors["Pressure 2"].get_br_uid()
        return self.sensors["Pressure 2"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_3(self):
        uid = self.sensors["Pressure 3"].get_br_uid()
        return self.sensors["Pressure 3"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_4(self):
        uid = self.sensors["Pressure 4"].get_br_uid()
        return self.sensors["Pressure 4"].read_sensor(self.brick_stack.get_device(uid))

    def read_temperature_1(self):
        uid = self.sensors["Temperatur Nitrous"].get_br_uid()
        return self.sensors["Temperatur Nitrous"].read_sensor(self.brick_stack.get_device(uid))

    def read_temperature_2(self):
        uid = self.sensors["Temperatur Engine"].get_br_uid()
        return self.sensors["Temperatur Engine"].read_sensor(self.brick_stack.get_device(uid))

    def read_load_cell_1(self):
        uid = self.sensors["Thrust load cell"].get_br_uid()
        return self.sensors["Thrust load cell"].read_sensor(self.brick_stack.get_device(uid))

    def read_load_cell_2(self):
        uid = self.sensors["Nitrous load cell"].get_br_uid()
        return self.sensors["Nitrous load cell"].read_sensor(self.brick_stack.get_device(uid))

    def read_differential_pressure(self):
        uid = self.sensors["Differential Nitrous pressure"].get_br_uid()
        return self.sensors["Differential Nitrous pressure"].read_sensor(self.brick_stack.get_device(uid))

    # ++++++
    # Internal methods
    # ++++++

    def _set_configuration(self):
        # we have to wait until the brick are there @TODO find out why
        sleep(0.5)
        for actor in self.actors.values():
            brick = self.brick_stack.get_device(actor.get_br_uid())

            match actor.type:
                case ActorType.LIGHT:
                    brick.set_configuration(actor.output,'o', False)
                    brick.set_configuration(actor.output + 1, 'o', False)
                    brick.set_configuration(actor.output + 2, 'o', False)
                case ActorType.HORN:
                    brick.set_configuration(actor.output, 'o', False)
                case ActorType.SERVO:
                    # with 0 is the position instantly set
                    velocity = 0
                    acceleration = 0
                    deceleration = 0
                    brick.set_motion_configuration(actor.output, velocity, acceleration, deceleration)


    def _construct_actors(self) -> None:
        """
        Construct all actors from the balrog.yaml
        """

        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config['actors']

            for actor in actors:
                # Convert actor type to ActorType enum
                actor_type = ActorType[actor['type'].upper()]
                self.actors[actor['name']] = Actor(
                    actor['name'], actor_type, actor['uid'], actor['output'], actor.get('inverted', False)
                )

        print(self.actors)

    def get_sensor_callback(self, name):
        """
        returns the sensor callbacks to register for the tinkerforge boards
        pressure 1 and 2 are on the same board, so we have to use the same callback
        the same of 3 and 4
        """
        match name:
            case "Pressure 0":
                return pressure_0_1_callback
            case "Pressure 1":
                return pressure_0_1_callback
            case "Pressure 2":
                return pressure_2_3_callback
            case "Differential Nitrous pressure":
                return pressure_2_3_callback
            case "Temperatur Engine":
                return temperature_engine_callback
            case "Temperatur Nitrous":
                return temperature_nitrous_callback
            case "Thrust load cell":
                return thrust_load_cell_callback
            case "Nitrous load cell":
                return nitrous_load_cell_callback
            case "N2OMainValveSensor" | "N2OFillValveSensor" | "N2OVentValveSensor" | "N2PurgeValveSensor" | "N2PressureValveSensor":
                return valve_sensor_callback
            case _:
                print(f"no callback found for {name}")
                self.event_queue.put({"type": EventType.INFO_EVENT, "message": f"No callback found for {name}"})
                return None

    def _construct_sensor(self) -> None:
        """
        construct all sensors from the balrog.yaml file
        """
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            sensors = balrog_config['sensors']

            for sensor in sensors:
                self.sensors[sensor['name']] = Sensor(sensor['name'],
                                                      sensor['type'],
                                                      sensor['uid'],
                                                      sensor['channel'],
                                                      self.get_sensor_callback(sensor['name']),
                                                      sensor['period'])
        print(self.sensors)

    # ++++++
    # Thread target
    # ++++++
    def _sequence_worker(self):
        if self.sequence is None:
            self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": "No sequence to execute."})
            return

        seq_idx = 0
        seq_ts = 0
        seq_len = len(self.sequence)

        for i in interval_timer.IntervalTimer(0.02):
            # signal used to abort the sequence with a button
            if self.thread_killer.is_set():
                return

            while seq_idx < seq_len and int(self.sequence[seq_idx][1]) <= seq_ts:
                tpl = self.sequence[seq_idx]
                self.actors[tpl[0]].action(tpl[2], self.brick_stack.get_device(self.actors[tpl[0]].get_br_uid()))
                seq_idx += 1

            if seq_idx >= seq_len:
                self.end_sequence()
                return

            seq_ts += 20
