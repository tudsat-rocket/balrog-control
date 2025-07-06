import os
import yaml

from threading import Thread
from typing import Any
from brick_handling import StackHandler
from control.definitions import ActorType
from test_definition_parsing import parse_csv
from actor import Actor
from definitions import ActorType

class Controller(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.actors = {}
        self._construct_actors()
        self.sequence = None
        self.brick_stack = StackHandler()
        Thread.start(self)


    # ++++++++++++
    # Gui API
    # ++++++++++++

    def connect(self, host: str, port: int) -> bool:
        self.brick_stack.start_connection()
        return True

    def stack_state(self) -> dict[str, Any]:
        pass

    def valve_state(self) -> dict[str, Any]:
        pass

    def self_check(self) -> bool:
        pass

    def test_light(self) -> bool:
        pass

    def test_horn(self) -> bool:
        pass

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
            #TODO: implement
            return True
        else:
            return False

    def abort(self) -> None:
        pass

    # ++++++
    # Internal methods
    # ++++++

    def _construct_actors(self) -> None:

        with open('../config/balrog.yaml', 'r') as f:
            balrog_config = yaml.load(f, Loader=yaml.SafeLoader)
            actors = balrog_config['actors']

            for actor in actors:
                self.actors[actor['name']] = Actor(actor['name'], actor['type'], actor['uid'], actor['output'])

        '''
        # Alternative static definition
        self.actors["Horn"] = Actor("Horn", actor_type=ActorType.HORN)
        self.actors["Light"] = Actor("Light", actor_type=ActorType.LIGHT)
        self.actors["Igniter"] = Actor("Igniter", actor_type=ActorType.TRIGGER)
        self.actors["NitrousMain"] = Actor("NitrousMain", actor_type=ActorType.SERVO)
        self.actors["NitrousVent"] = Actor("NitrousVent", actor_type=ActorType.SERVO)
        self.actors["NitrousFill"] = Actor("NitrousFill", actor_type=ActorType.SERVO)
        self.actors["N2Pressure"] = Actor("N2Pressure", actor_type=ActorType.SERVO)
        self.actors["N2Purge"] = Actor("N2Purge", actor_type=ActorType.SOLENOID)
        '''
