import os
from datetime import datetime
from time import sleep

import yaml
import interval_timer

from threading import Thread
from typing import Any
from control.brick_handling import StackHandler
from control.definitions import ActionType, EventType, ActorType
from control.test_definition_parsing import parse_csv
from control.actor import Actor
from control.sensor import Sensor
from queue import Queue
from control.dump_sensor_to_file import dump_sensor_to_file

from shared.shared_queues import *

def temperature_nitrous_callback( temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    #temperature_nitrous_sensor_queue.put(temperature)
    temperature_nitrous_sensor_list[0].append(datetime.now())
    temperature_nitrous_sensor_list[1].append(temperature)

def temperature_engine_callback( temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    #temperature_engine_sensor_queue.put(temperature)
    temperature_engine_sensor_list[0].append(datetime.now())
    temperature_engine_sensor_list[1].append(temperature)

def pressure_1_callback(channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    #pressure_1_sensor_queue.put(current)
    pressure_1_sensor_list[0].append(datetime.now())
    pressure_1_sensor_list[1].append(current)

def pressure_2_callback(channel, current):
    #print("Channel: " + str(channel))
    # print("Current: " + str(current / 1000000.0) + " mA")
    #pressure_2_sensor_queue.put(current)
    pressure_2_sensor_list[0].append(datetime.now())
    pressure_2_sensor_list[1].append(current)

def pressure_3_callback(channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    #pressure_3_sensor_queue.put(current)
    pressure_3_sensor_list[0].append(datetime.now())
    pressure_3_sensor_list[1].append(current)

def pressure_4_callback( channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    #pressure_4_sensor_queue.put(current)
    pressure_4_sensor_list[0].append(datetime.now())
    pressure_4_sensor_list[1].append(current)

def thrust_load_cell_callback( weight):
    #print("Weight thrust: " + str(weight) + " g")
    #load_cell_1_sensor_queue.put(weight)
    load_cell_1_sensor_list[0].append(datetime.now())
    load_cell_1_sensor_list[1].append(weight)

def nitrous_load_cell_callback(weight):
    #print("Weight nitrous: " + str(weight) + " g")
    #load_cell_2_sensor_queue.put(weight)
    load_cell_2_sensor_list[0].append(datetime.now())
    load_cell_2_sensor_list[1].append(weight)

def differential_pressure_callback( channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    #differential_pressure_queue.put(current)
    differential_pressure_list[0].append(datetime.now())
    differential_pressure_list[1].append(current)


class Controller(Thread):
    sensor_enabled = False
    connected = False
    servo_fill_open = False
    servo_vent_open = False
    servo_main_open = False
    abort_sequence = False

    def __init__(self, event_queue: Queue, thread_killer):
        Thread.__init__(self)
        self.actors = {}
        self.sensors = {}
        self._construct_actors()
        self._construct_sensor()
        self.brick_stack = StackHandler()
        self.sequence = None
        self.event_queue = event_queue
        self.thread_killer = thread_killer

    def run(self):
        super().run()
        self._sequence_worker()

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

    def test_light(self) -> bool:
        """
        toggles every light color for 1s and turns off all lights afterwards
        """
        uid = self.actors["Light"].get_br_uid()
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
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(uid))

    def set_light_to_yellow(self):
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid))

    def test_horn(self) -> bool:
        """
        trigger the horn
        """
        uid = self.actors["Horn"].get_br_uid()
        self.actors["Horn"].action(ActionType.SOUND_HORN, self.brick_stack.get_device(uid))
        return True

    def test_counter(self):
        """
        resets and start the counter on the segment display
        """
        uid = self.actors["SegmentDisplay"].get_br_uid()
        self.actors["SegmentDisplay"].action(ActionType.COUNTER_RESET, self.brick_stack.get_device(uid))
        self.actors["SegmentDisplay"].action(ActionType.COUNTER_START, self.brick_stack.get_device(uid))
        return True

    def test_servo_nitrous_main(self):
        """
        toggle the main valve from open to close
        """
        uid = self.actors["NitrousMain"].get_br_uid()
        if self.servo_main_open:
            self.actors["NitrousMain"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
            self.servo_main_open = False
        else:
            self.actors["NitrousMain"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
            self.servo_main_open = True

        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "main",
                              "state": self.servo_main_open,
                                }
                             )
        return True

    def test_servo_nitrous_vent(self):
        """
        toggle the vent between open to close
        """
        uid = self.actors["NitrousVent"].get_br_uid()
        if self.servo_vent_open:
            self.actors["NitrousVent"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
            self.servo_vent_open = False
        else:
            self.actors["NitrousVent"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
            self.servo_vent_open = True
        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "vent",
                              "state": self.servo_vent_open,
                              })

    def test_servo_nitrous_fill(self):
        """
        toggle the fill valve between open to close
        """
        uid = self.actors["NitrousFill"].get_br_uid()
        if self.servo_fill_open:
            self.actors["NitrousFill"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(uid))
            self.servo_fill_open = False
        else:
            self.actors["NitrousFill"].action(ActionType.SERVO_OPEN, self.brick_stack.get_device(uid))
            self.servo_fill_open = True
        self.event_queue.put({"type": EventType.VALVE_STATUS_UPDATE,
                              "valve": "fill",
                              "state": self.servo_fill_open,
                              })


    def load_test_definition(self, path: os.path) -> bool:
        if path is not None:
            self.sequence = parse_csv(path)
            return True
        else:
            print(f"Error {path} is not a valid path")
            return False

    def calibrate_thrust_load(self, weight):
        """
        calibrates the thurst load cell with the given weight
        """
        uid = self.sensors["Thrust load cell"].get_br_uid()
        return self.sensors["Thrust load cell"].calibrate_load(self.brick_stack.get_device(uid), weight)

    def calibrate_nitrous_load(self, weight):
        """
        calibrates the nitrous load cell with the given weight
        """
        uid = self.sensors["Nitrous load cell"].get_br_uid()
        return self.sensors["Nitrous load cell"].calibrate_load(self.brick_stack.get_device(uid), weight)

    def verify_sequence(self) -> bool:
        if self.sequence is None:
            return False

        for step in self.sequence:

            if step[0] not in self.actors.keys():
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
        if not self.sensor_enabled:
            print("enable all sensors")
            self.enable_all_sensor_callbacks()
            self.sensor_enabled = True
        else:
            print("disable all sensors")
            self.disable_all_sensor_callbacks()
            self.sensor_enabled = False

    def start_sequence(self) -> bool:
        """
        start the loaded sequence. Before the sequence is started, we trigger the horn and set the light on red
        """
        print("Start sequence...")
        if self.sequence is not None:
            self.event_queue.put({"type": EventType.SEQUENCE_STARTED})

            # --- prepare sequence ---
            self.set_light_to_yellow()
            # set light to red and trigger horn
            # this is to ensure that everyone is aware of the sequence
            print("Safety preparation")
            self.test_horn()
            self.set_light_to_red()
            print("Wait 5s for everyone to be away")
            sleep(5)

            # --- run sequence ---
            print("running sequence")
            # start the sequence
            self.enable_all_sensor_callbacks()
            self.run()
            self.disable_all_sensor_callbacks()

            # --- Finish sequence
            self.set_light_to_yellow()
            # wait a moment to ensure every callback is done
            # print("waiting for callbacks to complete...")
            # sleep(0.5)
            dump_sensor_to_file()
            self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
            return True
        else:
            self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": "No Sequence found. Please load a sequence first"})
            return False

    def abort(self) -> None:
        """
        abort the sequence
        """
        # stop the sequence worker
        self.abort_sequence = True

        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})

        # Close All Valves
        self.actors["NitrousMain"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["NitrousMain"]))
        self.actors["NitrousVent"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["NitrousVent"]))
        self.actors["NitrousFill"].action(ActionType.SERVO_CLOSE, self.brick_stack.get_device(self.actors["NitrousFill"]))

        # Open Purge Valve
        self.actors["N2Purge"].action(ActionType.SOLENOID_OPEN, self.brick_stack.get_device(self.actors["N2Purge"]))

        # visual and auditory warnings
        self.actors["Horn"].action(ActionType.SOUND_HORN, self.brick_stack.get_device(self.actors["Horn"]))
        self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(self.actors["Light"]))

        self.disable_all_sensor_callbacks()
        self.set_light_to_yellow()

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


    def _construct_actors(self) -> None:
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config['actors']

            for actor in actors:
                # print(actor)
                self.actors[actor['name']] = Actor(actor['name'], actor['type'], actor['uid'], actor['output'])

        print(self.actors)

    def get_sensor_callback(self, name):
        match name:
            case "Pressure 1":
                return pressure_1_callback
            case "Pressure 2":
                return pressure_2_callback
            case "Pressure 3":
                return pressure_3_callback
            case "Pressure 4":
                return pressure_4_callback
            case "Temperatur Engine":
                return temperature_engine_callback
            case "Temperatur Nitrous":
                return temperature_nitrous_callback
            case "Thrust load cell":
                return thrust_load_cell_callback
            case "Nitrous load cell":
                return nitrous_load_cell_callback
            case "Differential Nitrous pressure":
                return differential_pressure_callback
            case _:
                print(f"no callback found for {name}")

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

        seq_idx = 0
        seq_ts = 0
        seq_len = len(self.sequence)

        for i in interval_timer.IntervalTimer(0.02):

            if self.thread_killer.is_set():
                self.abort()
                break

            # signal used to abort the sequence with a button
            # @TODO check if that works
            if self.abort_sequence:
                break

            while int(self.sequence[seq_idx][1]) <= seq_ts:
                tpl = self.sequence[seq_idx]
                self.actors[tpl[0]].action(tpl[2], self.brick_stack.get_device(self.actors[tpl[0]].get_br_uid()))
                if seq_idx == seq_len-1:
                    return
                seq_idx += 1

            seq_ts += 20
