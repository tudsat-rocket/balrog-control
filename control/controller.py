import os
import yaml
import interval_timer

from threading import Thread
from typing import Any
from control.brick_handling import StackHandler
from control.definitions import ActionType, EventType
from control.test_definition_parsing import parse_csv
from control.actor import Actor
from control.sensor import Sensor
from queue import Queue

# from random import randint

class Controller(Thread):

    def __init__(self, event_queue: Queue):
        Thread.__init__(self)
        self.actors = {}
        self.sensors = {}
        self._construct_actors()
        self._construct_sensor()
        self.sequence = None
        self.brick_stack = StackHandler()
        self.event_queue = event_queue

    def run(self):
        super().run()

    def join(self, timeout = None):
        super().join()

    # ++++++++++++
    # Gui API
    # ++++++++++++

    def connect(self, host: str, port: int) -> bool:
        print(f"Connect to {host}:{port}")
        try:
            # @TODO the UI freezes while waiting for a new connection.
            self.brick_stack.start_connection(host, port)
            self.event_queue.put({"type": EventType.CONNECTION_STATUS_UPDATE,
                                  "status": "Connected",
                                  "hostname": host,
                                  "port": port}
                                 )
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
        return True

    def test_light(self) -> bool:
        uid = self.actors["Light"].get_br_uid()
        #self.actors["Light"].action(ActionType.LIGHT_GREEN, self.brick_stack.get_device(uid))
        self.actors["Light"].action(ActionType.LIGHT_ON, self.brick_stack.get_device(uid))
        return True

    def test_horn(self) -> bool:
        uid = self.actors["Horn"].get_br_uid()
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

    def start_sequence(self) -> bool:
        print("Start sequence...")
        self.event_queue.put({"type": EventType.SEQUENCE_STARTED}) # @TODO remove
        if self.sequence is not None:
            self.event_queue.put({"type": EventType.SEQUENCE_STARTED})
            self.run()
            self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
            return True
        else:
            self.event_queue.put({"type": EventType.SEQUENCE_ERROR, "message": "No Sequence found. Please load a sequence first"})
            return False

    def abort(self) -> None:
        self.event_queue.put({"type": EventType.SEQUENCE_STOPPED})
        # @TODO: implement
        pass

    def read_pressure_1(self):
        # return randint(0, 100)
        uid = self.sensors["Pressure 1"].get_br_uid()
        return self.sensors["Pressure 1"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_2(self):
        # return randint(0, 100)
        uid = self.sensors["Pressure 2"].get_br_uid()
        return self.sensors["Pressure 2"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_3(self):
        # return randint(0, 100)
        uid = self.sensors["Pressure 3"].get_br_uid()
        return self.sensors["Pressure 3"].read_sensor(self.brick_stack.get_device(uid))

    def read_pressure_4(self):
        # return randint(0, 100)
        uid = self.sensors["Pressure 4"].get_br_uid()
        return self.sensors["Pressure 4"].read_sensor(self.brick_stack.get_device(uid))

    def read_temperature_1(self):
        # return randint(0, 100)
        uid = self.sensors["Temperatur 1"].get_br_uid()
        return self.sensors["Temperatur 1"].read_sensor(self.brick_stack.get_device(uid))

    def read_temperature_2(self):
        # return randint(0, 100)
        uid = self.sensors["Temperatur 2"].get_br_uid()
        return self.sensors["Temperatur 2"].read_sensor(self.brick_stack.get_device(uid))

    def read_load_cell_1(self):
        # return randint(0, 100)
        uid = self.sensors["Load cell 1"].get_br_uid()
        return self.sensors["Load cell 1"].read_sensor(self.brick_stack.get_device(uid))

    def read_load_cell_2(self):
        # return randint(0, 100)
        uid = self.sensors["Load cell 2"].get_br_uid()
        return self.sensors["Load cell 2"].read_sensor(self.brick_stack.get_device(uid))

    def read_differential_pressure(self):
        # return randint(0, 100)
        uid = self.sensors["Differential pressure"].get_br_uid()
        return self.sensors["Differential pressure"].read_sensor(self.brick_stack.get_device(uid))

    # ++++++
    # Internal methods
    # ++++++

    def _construct_actors(self) -> None:
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config['actors']

            for actor in actors:
                # print(actor)
                self.actors[actor['name']] = Actor(actor['name'], actor['type'], actor['uid'], actor['output'])

        print(self.actors)

    def _construct_sensor(self) -> None:
        """
        construct all sensors from the balrog.yaml file
        """
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            sensors = balrog_config['sensors']

            for sensor in sensors:
                # print(sensor)
                self.sensors[sensor['name']] = Sensor(sensor['name'], sensor['type'], sensor['uid'], sensor['port'], sensor['pin'])
        print(self.sensors)

    # ++++++
    # Thread target
    # ++++++

    def _sequence_worker(self, thread_killer):

        seq_idx = 0

        for i in interval_timer.IntervalTimer(0.02):


            self.actors[self.sequence[seq_idx][0]].action()

            if thread_killer.is_set():
                break
