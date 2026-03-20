from datetime import datetime

from shared.shared_lists import (
    differential_pressure_list,
    cc_pressure_1_list,
    load_cell_1_sensor_list,
    load_cell_2_sensor_list,
    n2_pressure_valve_sensor_list,
    n2_purge_valve_sensor_list,
    n2o_fill_valve_sensor_list,
    n2o_main_valve_sensor_list,
    n2o_vent_valve_sensor_list,
    pressure_0_sensor_list,
    pressure_1_sensor_list,
    pressure_2_sensor_list,
    temperature_engine_sensor_list,
    temperature_nitrous_sensor_list,
)


def current_to_pressure(current):
    """Apply linear translation of current to pressure"""
    # 100 = m*20.006 - m*4.001 =
    # 6.248047485
    # 0 = 6.248047485*4.001 => 24.992191
    # => f(x) = 6.248047485*current-24.992191
    # @todo verify calculation
    return 6.248047485 * (current / 1000000.0) - 24.992191


def temperature_nitrous_callback(temperature):
    # print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_nitrous_sensor_list[0].append(datetime.now())
    temperature_nitrous_sensor_list[1].append(temperature / 100.0)


def temperature_engine_callback(temperature):
    # print("Temperature: " + str(temperature / 100.0) + " °C")
    temperature_engine_sensor_list[0].append(datetime.now())
    temperature_engine_sensor_list[1].append(temperature / 100.0)


def pressure_0_1_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    # print("----")
    if channel == 0:
        pressure_0_sensor_list[0].append(datetime.now())
        pressure_0_sensor_list[1].append(current_to_pressure(current))
    elif channel == 1:
        pressure_1_sensor_list[0].append(datetime.now())
        pressure_1_sensor_list[1].append(current_to_pressure(current))


def pressure_2_3_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    if channel == 0:
        differential_pressure_list[0].append(datetime.now())
        differential_pressure_list[1].append(current_to_pressure(current))
    elif channel == 1:
        pressure_2_sensor_list[0].append(datetime.now())
        pressure_2_sensor_list[1].append(current_to_pressure(current))

def pressure_4_callback(channel, current):
    # print(f"Channel {channel} Current: {str(current / 1000000.0)} mA")
    if channel == 0:
        cc_pressure_1_list[0].append(datetime.now())
        cc_pressure_1_list[1].append(current_to_pressure(current))


def thrust_load_cell_callback(weight):
    # print("Weight thrust: " + str(weight) + " g")
    load_cell_1_sensor_list[0].append(datetime.now())
    load_cell_1_sensor_list[1].append(weight / 1000.0)


def nitrous_load_cell_callback(weight):
    # print("Weight nitrous: " + str(weight) + " g")
    load_cell_2_sensor_list[0].append(datetime.now())
    load_cell_2_sensor_list[1].append(weight / 1000.0)


def valve_sensor_callback(channel, position):
    match channel:
        case 0:
            n2o_fill_valve_sensor_list[0].append(datetime.now())
            n2o_fill_valve_sensor_list[1].append(position)
            # @TODO(Nucleus): The use of a sigelton did not work here.
            # But the ideas was to move the server a bit back
            # as soon as it reached the max position to fix the issue
            # with a high power consumption
            # controller_singelton.adjust_valve_if_at_limit("N20FillValve", position)
        case 1:
            n2o_vent_valve_sensor_list[0].append(datetime.now())
            n2o_vent_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("N20VentValve", position)
        case 2:
            n2o_main_valve_sensor_list[0].append(datetime.now())
            n2o_main_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("N20MainValve", position)
        case 3:
            n2_pressure_valve_sensor_list[0].append(datetime.now())
            n2_pressure_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("N2PressureValve", position)
        case 4:
            n2_purge_valve_sensor_list[0].append(datetime.now())
            n2_purge_valve_sensor_list[1].append(position)
            # controller_singelton.adjust_valve_if_at_limit("N2PurgeValve", position)
