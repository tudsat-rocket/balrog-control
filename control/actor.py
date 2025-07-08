from typing import Any
from control.definitions import ActorType, ActionType

class Actor:
    """
    Abstract representation of an actor
    """

    def __init__(self, name: str = None, actor_type: ActorType = ActorType.DUMMY,
                 uid: str = None, output: int = 0):

        # human-readable name
        self.name = name
        self.type = actor_type
        # uid of bricklet responsible for controlling the actor 
        self.br_uid = uid
        # nr. of output in case of multiple outputs, 0 else
        self.output = output

    def set_actor_name(self, name: str) -> None:
        self.name = name
    
    def get_actor_type(self) -> ActorType:
        return self.type

    def set_actor_type(self, actor_type: ActorType) -> None:
        self.type = actor_type

    def get_br_uid(self) -> str:
        return self.br_uid 

    def set_br_uid(self, uid: str) -> None:
        self.br_uid = uid 

    def get_output(self):
        return self.output

    def set_output(self, output) -> None:
        self.output = output

    def action(self, action: ActionType, brick) -> None:
        match action:
            case ActionType.SOUND_HORN:
                return self.sound_horn(brick)
            case ActionType.SERVO_OPEN:
                return self.servo_open(brick)
            case ActionType.SERVO_CLOSE:
                return self.servo_close(brick)
            case ActionType.SERVO_TOGGLE:
                return self.servo_toggle(brick)
            case ActionType.SOLENOID_OPEN:
                return self.solenoid_open(brick)
            case ActionType.SOLENOID_CLOSE:
                return self.solenoid_close(brick)
            case ActionType.SOLENOID_TOGGLE:
                return self.solenoid_toggle(brick)
            case ActionType.PULL_TRIGGER:
                return self.pull_trigger(brick)
            case ActionType.RELEASE_TRIGGER:
                return self.release_trigger(brick)
            case ActionType.LIGHT_ON:
                return self.light_on(brick)
            case ActionType.LIGHT_OFF:
                return self.light_off(brick)
            case ActionType.LIGHT_GREEN:
                return self.light_green()
            case ActionType.LIGHT_YELLOW:
                return self.light_yellow()
            case ActionType.LIGHT_RED:
                return self.light_red()
            case _:
                raise NotImplementedError

    def servo_open(self, servo_bricklet) -> None:
        pass

    def servo_close(self, servo_bricklet) -> None:
        pass

    def servo_toggle(self, servo_bricklet) -> None:
        pass

    def solenoid_open(self, brick) -> None:
        pass

    def solenoid_close(self, brick) -> None:
        pass

    def solenoid_toggle(self, brick) -> None:
        pass

    def sound_horn(self, ac_bricklet) -> None:
        ac_bricklet.set_monflop(self.output, True, 1000) # sound horn for 1s = 1000ms

    def light_on(self, brick) -> None:
        pass

    def light_off(self, brick) -> None:
        pass

    def light_toggle(self, brick) -> None:
        pass

    def light_green(self) -> None:
        pass

    def light_yellow(self) -> None:
        pass

    def light_red(self) -> None:
        pass

    def pull_trigger(self, brick) -> None:
        pass

    def release_trigger(self, brick) -> None:
        pass
