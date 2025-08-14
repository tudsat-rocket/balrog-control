import os
from datetime import time
from time import sleep
from unittest import case

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

from shared.shared_queues import *

def temperature_nitrous_callback( temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_nitrous_sensor_queue.put(temperature)

def temperature_engine_callback( temperature):
    #print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_engine_sensor_queue.put(temperature)

def pressure_1_callback(channel, current):
    print("Channel: " + str(channel))
    print("Current: " + str(current / 1000000.0) + " mA")
    pressure_1_sensor_queue.put(current)

def pressure_2_callback(channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    pressure_2_sensor_queue.put(current)

def pressure_3_callback(channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    pressure_3_sensor_queue.put(current)

def pressure_4_callback( channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    pressure_4_sensor_queue.put(current)

def thrust_load_cell_callback( weight):
    #print("Weight: " + str(weight) + " g")
    load_cell_1_sensor_queue.put(weight)

def nitrous_load_cell_callback( weight):
    #print("Weight: " + str(weight) + " g")
    load_cell_2_sensor_queue.put(weight)

def differential_pressure_callback( channel, current):
    #print("Channel: " + str(channel))
    #print("Current: " + str(current / 1000000.0) + " mA")
    differential_pressure_queue.put(current)


class Controller(Thread):
    sensor_enabled = False
    connected = False

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
        uid = self.actors["Light"].get_br_uid()
        self.actors["Light"].action(ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_YELLOW, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_RED, self.brick_stack.get_device(uid))
        sleep(1)
        self.actors["Light"].action(ActionType.LIGHT_OFF, self.brick_stack.get_device(uid))

        return True

    def test_horn(self) -> bool:
        print("test horn")
        uid = self.actors["Horn"].get_br_uid()
        print(uid)
        self.actors["Horn"].action(ActionType.SOUND_HORN, self.brick_stack.get_device(uid))
        return True

    def load_test_definition(self, path: os.path) -> bool:
        if path is not None:
            self.sequence = parse_csv(path)
            return True
        else:
            return False

    def verify_sequence(self) -> bool:
        if self.sequence is None:
            return False

        for step in self.sequence:

            if step[0] not in self.actors.keys():
                return False

        return True

    def enable_all_callbacks(self):
        """
        Enable the callbacks and start the sensor reading
        """
        print("enable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            sensor.enable_callback(self.brick_stack.get_device(uid))

    def disable_all_callbacks(self):
        """
        Disable all callbacks. No new sensor values will be added
        """
        print("disable sensors")
        for sensor in self.sensors.values():
            uid = sensor.get_br_uid()
            sensor.disable_callback(self.brick_stack.get_device(uid))

    def toggle_sensors(self):
        """
        Toggles the sensor callbacks on and off.
        """
        if not self.sensor_enabled:
            print("enable all sensors")
            self.enable_all_callbacks()
            self.sensor_enabled = True
        else:
            print("disable all sensors")
            self.disable_all_callbacks()
            self.sensor_enabled = False

    def start_sequence(self) -> bool:
        print("Start sequence...")
        # self.event_queue.put({"type": EventType.SEQUENCE_STARTED}) # @TODO remove
        if self.sequence is not None:
            self.event_queue.put({"type": EventType.SEQUENCE_STARTED})
            self.enable_all_callbacks()
            self.run()
            self.disable_all_callbacks()
            self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
            return True
        else:
            self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": "No Sequence found. Please load a sequence first"})
            return False

    def abort(self) -> None:
        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
        self.disable_all_callbacks()
        # @TODO: implement
        pass

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
                                                      sensor['periode'])
        print(self.sensors)

    # ++++++
    # Thread target
    # ++++++
    def _sequence_worker(self, thread_killer):

        seq_idx = 0
        seq_ts = 0

        for i in interval_timer.IntervalTimer(0.02):

            if self.thread_killer.is_set():
                self.abort()
                break

            while self.sequence[seq_idx][1] <= seq_ts:
                tpl = self.sequence[seq_idx]
                tpl[0].action(tpl[2], tpl.get_br_uid())
                seq_idx += 1

            seq_ts += 20
