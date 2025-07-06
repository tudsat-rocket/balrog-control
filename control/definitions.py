from enum import Enum, StrEnum, IntEnum

class ActorType(StrEnum):
    DUMMY = "DUMMY"
    SERVO = "SERVO"
    SOLENOID = "SOLENOID"
    HORN = "HORN"
    LIGHT = "LIGHT"
    TRIGGER = "TRIGGER"


class SensorType(StrEnum):
    PRESSURE = "PRESSURE"
    TEMPERATURE = "TEMPERATURE"
    LOAD = "LOAD"


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
        case _:
            return ActionType.NOT_IMPLEMENTED

