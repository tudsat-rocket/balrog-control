from enum import StrEnum, IntEnum

class ActorType(StrEnum):
    DUMMY = "DUMMY"
    SERVO = "SERVO"
    SOLENOID = "SOLENOID"
    HORN = "HORN"
    LIGHT = "LIGHT"
    COUNTER = "COUNTER"
    TRIGGER = "TRIGGER"

class SensorType(StrEnum):
    DUMMY = "DUMMY"
    PRESSURE = "PRESSURE"
    TEMPERATURE = "TEMPERATURE"
    LOAD = "LOAD"
    DIFFERENTIAL_PRESSURE = "DIFFERENTIAL_PRESSURE"

class ActionType(IntEnum):
    NOT_IMPLEMENTED = -1 
    SERVO_OPEN = 1
    SERVO_CLOSE = 2
    SERVO_TOGGLE = 3
    SOLENOID_OPEN = 4
    SOLENOID_CLOSE = 5
    SOLENOID_TOGGLE = 6
    SOUND_HORN = 7 
    LIGHT_ON = 8
    LIGHT_OFF = 9
    TOGGLE_LIGHT = 10
    LIGHT_GREEN = 11
    LIGHT_YELLOW = 12
    LIGHT_RED = 13
    PULL_TRIGGER = 14
    RELEASE_TRIGGER = 15
    COUNTER_START = 16
    COUNTER_STOP = 17
    COUNTER_RESET = 18
    SERVO_OPEN_SLOW = 19
    SERVO_SAFE_OPEN = 20
    SERVO_OPEN_QUARTER_SLOW = 21

def str_to_action(action: str) -> ActionType:

    match action:
        case "SERVO_OPEN":
            return ActionType.SERVO_OPEN
        case "SERVO_CLOSE":
            return ActionType.SERVO_CLOSE
        case "SERVO_TOGGLE":
            return ActionType.SERVO_TOGGLE
        case "SOLENOID_OPEN":
            return ActionType.SOLENOID_OPEN
        case "SOLENOID_CLOSE":
            return ActionType.SOLENOID_CLOSE
        case "SOLENOID_TOGGLE":
            return ActionType.SOLENOID_TOGGLE
        case "SOUND_HORN":
            return ActionType.SOUND_HORN
        case "LIGHT_ON":
            return ActionType.LIGHT_ON
        case "LIGHT_OFF":
            return ActionType.LIGHT_OFF
        case "TOGGLE_LIGHT":
            return ActionType.TOGGLE_LIGHT
        case "LIGHT_GREEN":
            return ActionType.LIGHT_GREEN
        case "LIGHT_YELLOW":
            return ActionType.LIGHT_YELLOW
        case "LIGHT_RED":
            return ActionType.LIGHT_RED
        case "PULL_TRIGGER":
            return ActionType.PULL_TRIGGER
        case "RELEASE_TRIGGER":
            return ActionType.RELEASE_TRIGGER
        case "COUNTER_START":
            return ActionType.COUNTER_START
        case "COUNTER_STOP":
            return ActionType.COUNTER_STOP
        case "COUNTER_RESET":
            return ActionType.COUNTER_RESET
        case "SERVO_OPEN_SLOW":
            return ActionType.SERVO_OPEN_SLOW
        case "SERVO_SAFE_OPEN":
            return ActionType.SERVO_SAFE_OPEN
        case "SERVO_OPEN_QUARTER_SLOW":
            return ActionType.SERVO_OPEN_QUARTER_SLOW
        case _:
            return ActionType.NOT_IMPLEMENTED

class EventType(StrEnum):
    CONNECTION_STATUS_UPDATE = "STATUS_UPDATE"
    INFO_EVENT = "INFO_EVENT"
    CONFIRMATION_EVENT = "CONFIRMATION_EVENT"
    VALVE_STATUS_UPDATE = "VALVE_STATUS_UPDATE"
    SEQUENCE_STARTED = "SEQUENCE_STARTED"
    SEQUENCE_STOPPED = "SEQUENCE_STOPPED"
    SEQUENCE_ERROR = "SEQUENCE_ERROR"
    STATE_CHANGE = "STATE_CHANGE"


class State(StrEnum):
    GREEN_STATE = "GREEN_STATE"
    YELLOW_STATE = "YELLOW_STATE"
    RED_STATE = "RED_STATE"