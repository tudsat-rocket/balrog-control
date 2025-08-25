import time
from time import sleep

from control.definitions import ActorType, ActionType

class Actor:
    """
    Abstract representation of an actor
    """

    def __init__(self, name: str = "", actor_type: ActorType = ActorType.DUMMY,
                 uid: str = "", output: int = 0, inverted: bool = False):

        # human-readable name
        self.name = name
        self.type = actor_type
        # uid of bricklet responsible for controlling the actor 
        self.br_uid = uid
        # nr. of output in case of multiple outputs, 0 else
        self.output = output
        # whether the actor is inverted
        self.inverted = inverted

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
            case ActionType.SERVO_OPEN_SLOW:
                return self.servo_open_slow(brick)
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
            case ActionType.LIGHT_ALL:
                return self.light_all(brick)
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
        """
        opens the servo to 90°
        """
        position = 9000  # 9000/100 degrees => 90 degrees
        if self.inverted:
            position *= -1
        servo_bricklet.set_position(self.get_output(), position)
        servo_bricklet.set_enable(self.get_output(), True)
        sleep(1) #@TODO display servo after use?
        servo_bricklet.set_enable(self.get_output(), False)

    def servo_open_slow(self, servo_bricklet):
        """
        open the servo to 90° within 2s
        """
        # @TODO test implementation
        servo_bricklet.set_enable(self.get_output(), True)
        for i in range(9000):  # 9000/100 degrees => 90 degrees
            position = i if not self.inverted else -i
            servo_bricklet.set_position(self.get_output(), position)
            # to slow down the servo opening
            sleep(0.00022)  # 2s/9000 steps = 2s until open

    def servo_open_quarter_slow(self, servo_bricklet):
        servo_bricklet.set_enable(self.get_output(), True)
        for i in range(2250):  # 2250/100 degrees => 22.5 degrees => 1/4 open
            position = i if not self.inverted else -i
            servo_bricklet.set_position(self.get_output(), position)
            # to slow down the servo opening
            sleep(0.00088)  # 2s/2250 steps = 2s until open
        # @TODO disable servo after use?

    def servo_safe_open(self, servo_bricklet) -> None:
        """
        Opens the servo to 90° until the current reaches a tested threshold of 5.
        We assume that a high current means the servo reached the end stop.
        """
        current = 0
        position = 0
        max_position = 9000
        servo_bricklet.set_enable(self.get_output(), True)
        while current < 5:
            servo_bricklet.set_position(self.get_output(), position)
            if self.inverted:
                position -= 1
            else:
                position += 1

            if abs(position) > max_position:
                break

            current = servo_bricklet.get_servo_current(self.get_output())

    def servo_close(self, servo_bricklet) -> None:
        position = 0  # Example position for close
        if self.inverted:
            position *= -1
        servo_bricklet.set_position(self.get_output(), position)
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
        brick.set_monoflop(self.output, True, 5000) # sound horn for 5s = 5000ms

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

    def light_all(self, brick) -> None:
        brick.set_selected_value(self.output, True)
        brick.set_selected_value(self.output + 1, True)
        brick.set_selected_value(self.output + 2, True)

    def pull_trigger(self, brick) -> None:
        pass

    def release_trigger(self, brick) -> None:
        pass

    def counter_start(self, segment_display_brick) -> None:
        segment_display_brick.start_counter(0, 9999, 1, 10)

    def counter_stop(self, segment_display_brick) -> None:
        segment_display_brick.set_numeric_value(segment_display_brick.get_numeric_value(), 0)

    def counter_reset(self, segment_display_brick) -> None:
        segment_display_brick.set_numeric_value([0,0,0,0])
