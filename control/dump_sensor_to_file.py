import csv
import os
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


def get_value_or_minus(index, list):
    if index >= len(list[0]):
        return [-1, 1]
    else:
        return list[1][index]


def get_time_or_minus(index, list):
    if index >= len(list[0]):
        return [-1, 1]
    else:
        return list[0][index]


def dump_sensor_to_file():
    print("Dumping sensor data to file...")
    # create log folder if not exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    current_log_filename = f"dump_{timestamp}.csv"
    filepath = os.path.join("logs", current_log_filename)
    with open(filepath, "w", newline="") as file:
        log_file = file
        writer = csv.writer(log_file)
        writer.writerow(
            [
                "Time pressure 0",
                "pressure_0",
                "Time pressure 1",
                "pressure_1",
                "Time pressure 2",
                "pressure_2",
                "Time temperature Nitrous",
                "Temperature Nitrous",
                "Time Engine",
                "temperature_engine",
                "Time load cell",
                "load_cell_thrust",
                "Time load_cell_ox",
                "load_cell_ox",
                "Time CC0",
                "pressure_cc0",
                "Time CC1",
                "pressure_cc1",
                "Time N2OMainValve",
                "N2OValveState",
                "Time N2Ofill_valve",
                "N2Ofill_valveState",
                "Time N2OVentValve",
                "N2OVentValveState",
                "Time purge_valve",
                "purge_valveState",
                "TIme pressurization_valve",
                "pressurization_valveState",
            ]
        )
        time = 0

        # find max length of sensors
        length_pressure0 = len(pressure_0_sensor_list[1])
        length_pressure1 = len(pressure_1_sensor_list[1])
        length_pressure2 = len(pressure_2_sensor_list[1])
        length_temperature_nitrous = len(temperature_ox_sensor_list[1])
        length_temperature_engine = len(temperature_engine_sensor_list[1])
        length_loadcell_1 = len(load_cell_thrust_sensor_list[1])
        length_loadcell_2 = len(load_cell_ox_sensor_list[1])
        length_differential = len(cc_pressure_0_sensor_list[1])
        length_cc1 = len(cc_pressure_1_sensor_list[1])
        length_n2o_main_valve = len(main_valve_sensor_list[1])
        length_n2o_fill_valve = len(fill_valve_sensor_list[1])
        length_n2o_vent_valve = len(vent_valve_sensor_list[1])
        length_n2_purge_valve = len(purge_valve_sensor_list[1])
        length_n2_pressure_valve = len(pressurization_valve_sensor_list[1])
        max_length = max(
            [
                length_pressure0,
                length_pressure1,
                length_pressure2,
                length_temperature_nitrous,
                length_temperature_engine,
                length_loadcell_1,
                length_loadcell_2,
                length_differential,
                length_cc1,
                length_n2o_fill_valve,
                length_n2o_main_valve,
                length_n2o_vent_valve,
                length_n2_purge_valve,
                length_n2_pressure_valve,
            ]
        )

        for i in range(max_length):
            writer.writerow(
                [
                    get_time_or_minus(i, pressure_0_sensor_list),
                    get_value_or_minus(i, pressure_0_sensor_list),
                    get_time_or_minus(i, pressure_1_sensor_list),
                    get_value_or_minus(i, pressure_1_sensor_list),
                    get_time_or_minus(i, pressure_2_sensor_list),
                    get_value_or_minus(i, pressure_2_sensor_list),
                    get_time_or_minus(i, temperature_ox_sensor_list),
                    get_value_or_minus(i, temperature_ox_sensor_list),
                    get_time_or_minus(i, temperature_engine_sensor_list),
                    get_value_or_minus(i, temperature_engine_sensor_list),
                    get_time_or_minus(i, load_cell_thrust_sensor_list),
                    get_value_or_minus(i, load_cell_thrust_sensor_list),
                    get_time_or_minus(i, load_cell_ox_sensor_list),
                    get_value_or_minus(i, load_cell_ox_sensor_list),
                    get_time_or_minus(i, cc_pressure_0_sensor_list),
                    get_value_or_minus(i, cc_pressure_0_sensor_list),
                    get_time_or_minus(i, cc_pressure_1_sensor_list),
                    get_value_or_minus(i, cc_pressure_1_sensor_list),
                    get_time_or_minus(i, main_valve_sensor_list),
                    get_value_or_minus(i, main_valve_sensor_list),
                    get_time_or_minus(i, fill_valve_sensor_list),
                    get_value_or_minus(i, fill_valve_sensor_list),
                    get_time_or_minus(i, vent_valve_sensor_list),
                    get_value_or_minus(i, vent_valve_sensor_list),
                    get_time_or_minus(i, purge_valve_sensor_list),
                    get_value_or_minus(i, purge_valve_sensor_list),
                    get_time_or_minus(i, pressurization_valve_sensor_list),
                    get_value_or_minus(i, pressurization_valve_sensor_list),
                ]
            )

            time += 5
        log_file.close()
        print("Finished dumping sensor data to file")
