import os
import yaml
import interval_timer

from threading import Thread
from typing import Any
from control.brick_handling import StackHandler
from control.definitions import ActorType, ActionType
from control.test_definition_parsing import parse_csv
from control.actor import Actor
from control.sensor import Sensor

class Controller(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.actors = {}
        self.sensors = {}
        self._construct_actors()
        self._construct_sensor()
        self.sequence = None
        self.brick_stack = StackHandler()

    def run(self):
        super().run()

    def join(self, timeout = None):
        super().join()

    # ++++++++++++
    # Gui API
    # ++++++++++++

    def connect(self, host: str, port: int) -> bool:
        print(f"Connect to {host}:{port}")
        self.brick_stack.start_connection(host, port)
        return True

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
        if self.sequence is not None:
            self.run()
            return True
        else:
            return False

    def abort(self) -> None:
        pass

    # ++++++
    # Internal methods
    # ++++++

    def _construct_actors(self) -> None:
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config['actors']

            for actor in actors:
                print(actor)
                self.actors[actor['name']] = Actor(actor['name'], actor['type'], actor['uid'], actor['output'])

    def _construct_sensor(self) -> None:
        """
        construct all sensors from the balrog.yaml file
        """
        with open('config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            sensors = balrog_config['sensors']

            for sensor in sensors:
                print(sensor)
                self.actors[sensor['name']] = Sensor(sensor['name'], sensor['type'], sensor['uid'], sensor['pin'])


    # ++++++
    # Thread target
    # ++++++

    def _sequence_worker(self, thread_killer):

        seq_idx = 0

        for i in interval_timer.IntervalTimer(0.02):


            self.actors[self.sequence[seq_idx][0]].action()

            if thread_killer.is_set():
                break
