from datetime import datetime
import os
import csv
from shared.shared_queues import *

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
    current_log_filename = f"log_{timestamp}.csv"
    filepath = os.path.join("logs", current_log_filename)
    log_file = open(filepath, "w", newline="")
    writer = csv.writer(log_file)
    writer.writerow(["Time pressure 0", "Pressure 0",
                     "Time pressure 1", "Pressure 1",
                     "Time pressure 2", "Pressure 2",
                     "Time temperature Nitrous", "Temperatur Nitrous",
                     "Time Engine", "Temperatur Engine",
                     "Time load cell", "Thrust load cell",
                     "Time Nitrous load cell", "Nitrous load cell",
                     "Time Differential", "Differential Nitrous pressure",
                     "Time N2OMainValve", "N2OValveState",
                     "Time N2OFillValve", "N2OFillValveState",
                     "Time N2OVentVavlve", "N2OVentValveState",
                     "Time N2PurgeValve", "N2PurgeValveState",
                     "TIme N2PressureValve", "N2PressureValveState"])
    time = 0

    # find max length of sensors
    length_pressure0 = len(pressure_0_sensor_list[1])
    length_pressure1 = len(pressure_1_sensor_list[1])
    length_pressure2 = len(pressure_2_sensor_list[1])
    length_temperature_nitrous = len(temperature_nitrous_sensor_list[1])
    length_temperature_engine = len(temperature_engine_sensor_list[1])
    length_loadcell_1 = len(load_cell_1_sensor_list[1])
    length_loadcell_2 = len(load_cell_2_sensor_list[1])
    length_differential = len(differential_pressure_list[1])
    length_n2o_main_valve = len(n2o_main_valve_sensor_list[1])
    length_n2o_fill_valve = len(n2o_fill_valve_sensor_list[1])
    length_n2o_vent_valve = len(n2o_vent_valve_sensor_list[1])
    length_n2_purge_valve = len(n2_purge_valve_sensor_list[1])
    length_n2_pressure_valve = len(n2_pressure_valve_sensor_list[1])
    max_length = max([length_pressure0, length_pressure1, length_pressure2, length_temperature_nitrous, length_temperature_engine, length_loadcell_1, length_loadcell_2, length_differential, length_n2o_fill_valve, length_n2o_main_valve, length_n2o_vent_valve, length_n2_purge_valve, length_n2_pressure_valve])


    for i in range(max_length):
        writer.writerow([
            get_time_or_minus(i, pressure_0_sensor_list),
            get_value_or_minus(i, pressure_0_sensor_list),

            get_time_or_minus(i, pressure_1_sensor_list),
            get_value_or_minus(i, pressure_1_sensor_list),

            get_time_or_minus(i, pressure_2_sensor_list),
            get_value_or_minus(i, pressure_2_sensor_list),

            get_time_or_minus(i, temperature_nitrous_sensor_list),
            get_value_or_minus(i, temperature_nitrous_sensor_list),

            get_time_or_minus(i, temperature_engine_sensor_list),
            get_value_or_minus(i, temperature_engine_sensor_list),

            get_time_or_minus(i,load_cell_1_sensor_list ),
            get_value_or_minus(i,load_cell_1_sensor_list ),

            get_time_or_minus(i,load_cell_2_sensor_list),
            get_value_or_minus(i,load_cell_2_sensor_list ),

            get_time_or_minus(i, differential_pressure_list),
            get_value_or_minus(i, differential_pressure_list),

            get_time_or_minus(i, n2o_main_valve_sensor_list),
            get_value_or_minus(i, n2o_main_valve_sensor_list),  

            get_time_or_minus(i, n2o_fill_valve_sensor_list),
            get_value_or_minus(i, n2o_fill_valve_sensor_list),

            get_time_or_minus(i, n2o_vent_valve_sensor_list),
            get_value_or_minus(i, n2o_vent_valve_sensor_list),

            get_time_or_minus(i, n2_purge_valve_sensor_list),
            get_value_or_minus(i, n2_purge_valve_sensor_list),

            get_time_or_minus(i, n2_pressure_valve_sensor_list),
            get_value_or_minus(i, n2_pressure_valve_sensor_list),
        ])

        time += 5
    log_file.close()