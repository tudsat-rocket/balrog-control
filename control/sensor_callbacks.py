from datetime import datetime

from shared.shared_lists import (
    cc_pressure_0_sensor_list,
    cc_pressure_1_sensor_list,
    load_cell_thrust_sensor_list,
    load_cell_ox_sensor_list,
    pressurization_valve_sensor_list,
    purge_valve_sensor_list,
    fill_valve_sensor_list,
    main_valve_sensor_list,
    vent_valve_sensor_list,
    pressure_0_sensor_list,
    pressure_1_sensor_list,
    pressure_2_sensor_list,
    temperature_engine_sensor_list,
    temperature_ox_sensor_list,
)


def current_to_pressure_100bar(current):
    return 6.248047485 * (current / 1000000.0) - 24.992191

def current_to_pressure_160bar(current):
    return 10.029461543 * (current / 1000000.0) - 40.12


def temperature_ox_callback(temperature):
    # print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_ox_sensor_list[0].append(datetime.now())
    temperature_ox_sensor_list[1].append(temperature / 100.0)


def temperature_engine_callback(temperature):
    # print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_engine_sensor_list[0].append(datetime.now())
    temperature_engine_sensor_list[1].append(temperature / 100.0)


def pressure_0_1_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    # print("----")
    if channel == 0:
        pressure_0_sensor_list[0].append(datetime.now())
        pressure_0_sensor_list[1].append(current_to_pressure_100bar(current))
    elif channel == 1:
        pressure_1_sensor_list[0].append(datetime.now())
        pressure_1_sensor_list[1].append(current_to_pressure_100bar(current))


def pressure_2_3_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    if channel == 0:
        cc_pressure_0_sensor_list[0].append(datetime.now())
        cc_pressure_0_sensor_list[1].append(current_to_pressure_160bar(current))
    elif channel == 1:
        pressure_2_sensor_list[0].append(datetime.now())
        pressure_2_sensor_list[1].append(current_to_pressure_100bar(current))

def pressure_4_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    if channel == 0:
        cc_pressure_1_sensor_list[0].append(datetime.now())
        cc_pressure_1_sensor_list[1].append(current_to_pressure_160bar(current))


def load_cell_thrust_callback(weight):
    # print("Weight thrust: " + str(weight) + " g")
    load_cell_thrust_sensor_list[0].append(datetime.now())
    load_cell_thrust_sensor_list[1].append(weight / 1000.0)


def load_cell_ox_callback(weight):
    # print("Weight nitrous: " + str(weight) + " g")
    load_cell_ox_sensor_list[0].append(datetime.now())
    load_cell_ox_sensor_list[1].append(weight / 1000.0)


def valve_sensor_callback(channel, position):
    match channel:
        case 0:
            fill_valve_sensor_list[0].append(datetime.now())
            fill_valve_sensor_list[1].append(position)
            # @TODO(Nucleus): The use of a sigelton did not work here.
            # But the ideas was to move the server a bit back
            # as soon as it reached the max position to fix the issue
            # with a high power consumption
            # controller_singelton.adjust_valve_if_at_limit("fill_valve", position)
        case 1:
            vent_valve_sensor_list[0].append(datetime.now())
            vent_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("VentValve", position)
        case 2:
            main_valve_sensor_list[0].append(datetime.now())
            main_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("main_valve", position)
        case 3:
            pressurization_valve_sensor_list[0].append(datetime.now())
            pressurization_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("pressurization_valve", position)
        case 4:
            purge_valve_sensor_list[0].append(datetime.now())
            purge_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("purge_valve", position)
