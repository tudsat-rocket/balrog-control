import time

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
                print("sound horn")
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
                return self.light_green(brick)
            case ActionType.LIGHT_YELLOW:
                return self.light_yellow(brick)
            case ActionType.LIGHT_RED:
                return self.light_red(brick)
            case ActionType.COUNTER_START:
                return self.counter_start(brick)
            case ActionType.COUNTER_RESET:
                return self.counter_reset(brick)
            case _:
                raise NotImplementedError

    def check(self, brick):
        match self.type:
            case ActorType.SERVO:
                self.action(ActionType.SERVO_OPEN, brick)
                time.sleep(1)
                self.action(ActionType.SERVO_CLOSE, brick)
                return True
            case ActorType.SOLENOID:
                self.action(ActionType.SOLENOID_OPEN, brick)
                time.sleep(1)
                self.action(ActionType.SOLENOID_CLOSE, brick)
                return True
            case ActorType.HORN:
                self.action(ActionType.SOUND_HORN, brick)
                return True
            case ActorType.LIGHT:
                self.action(ActionType.LIGHT_ON, brick)
                time.sleep(1.0)
                self.action(ActionType.LIGHT_OFF, brick)
                return True
            case ActorType.TRIGGER:
                # Dangerous, do not execute anything
                return True
            case ActorType.COUNTER:
                self.action(ActionType.COUNTER_START, brick)
                time.sleep(0.1)
                self.action(ActionType.COUNTER_RESET, brick)
                return True
            case _:
                return False

    def servo_open(self, servo_bricklet) -> None:
        servo_bricklet.set_position(self.get_output(), 9000) # 9000/100 degrees => 90 degrees
        servo_bricklet.set_enable(self.get_output(), True)

    def servo_close(self, servo_bricklet) -> None:
        servo_bricklet.set_position(self.get_output(), 0) # 0/100 degrees => 0 degrees
        servo_bricklet.set_enable(self.get_output(), True)

    def servo_toggle(self, servo_bricklet) -> None:
        pass

    def solenoid_open(self, io_brick) -> None:
        io_brick.set_selected_value(self.get_output(), True)

    def solenoid_close(self, io_brick) -> None:
        io_brick.set_selected_value(self.get_output(), False)

    def solenoid_toggle(self, brick) -> None:
        pass

    def sound_horn(self, brick) -> None:
        brick.set_monoflop(self.output, True, 5000) # sound horn for 1s = 1000ms

    def light_on(self, brick) -> None:
        # not used anymore
        pass

    def light_off(self, brick) -> None:
        brick.set_selected_value(self.output, False)
        brick.set_selected_value(self.output, False)
        brick.set_selected_value(self.output + 2, False)

    def light_toggle(self, brick) -> None:
        pass

    def light_green(self, brick) -> None:
        brick.set_selected_value(self.output + 2, True)
        # turn all other off
        brick.set_selected_value(self.output + 0, False)
        brick.set_selected_value(self.output + 1, False)

    def light_yellow(self, brick) -> None:
        # turn red light on
        brick.set_selected_value(self.output +1, True)
        # turn all other off
        brick.set_selected_value(self.output + 0, False)
        brick.set_selected_value(self.output + 2, False)

    def light_red(self, brick) -> None:
        # turn red light on
        brick.set_selected_value(self.output, True)
        # turn all other off
        brick.set_selected_value(self.output + 1, False)
        brick.set_selected_value(self.output + 2, False)

    def pull_trigger(self, brick) -> None:
        pass

    def release_trigger(self, brick) -> None:
        pass

    def counter_start(self, segment_display_brick) -> None:
        segment_display_brick.start_counter(0, 9999, 1, 100)

    def counter_stop(self, segment_display_brick) -> None:
        segment_display_brick.set_numeric_value(segment_display_brick.get_numeric_value(), 0)

    def counter_reset(self, segment_display_brick) -> None:
        segment_display_brick.set_numeric_value([0,0,0,0])
