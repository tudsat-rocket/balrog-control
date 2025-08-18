from datetime import datetime
import os
import csv
from shared.shared_queues import *

def get_value_or_minus(index, list):
    if index >= len(list):
        return [-1, 1]
    else:
        return list[1][index]

def get_time_or_minus(index, list):
    if index >= len(list):
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
    writer.writerow(["Time pressure2", "Pressure 2",
                     "Time pressure 3", "Pressure 3",
                     "Time pressure 4", "Pressure 4",
                     "Time temperature Nitrous", "Temperatur Nitrous",
                     "Time Engine", "Temperatur Engine",
                     "Time load cell", "Thrust load cell",
                     "Time Nitrous load cell", "Nitrous load cell",
                     "Time Differential", "Differential Nitrous pressure"])
    time = 0

    # find max length of sensors
    length_pressure2 = len(pressure_2_sensor_list)
    length_pressure3 = len(pressure_3_sensor_list)
    length_pressure4 = len(pressure_4_sensor_list)
    length_temperature_nitrous = len(temperature_nitrous_sensor_list)
    length_temperature_engine = len(temperature_engine_sensor_list)
    length_loadcell_1 = len(load_cell_1_sensor_list)
    length_loadcell_2 = len(load_cell_2_sensor_list)
    length_differential = len(differential_pressure_list)
    max_length = max([length_pressure2, length_pressure3, length_pressure4, length_temperature_nitrous, length_temperature_engine, length_loadcell_1, length_loadcell_2, length_differential])


    for i in range(max_length):
        writer.writerow([
            get_time_or_minus(i, pressure_2_sensor_list),
            get_value_or_minus(i, pressure_2_sensor_list),

            get_time_or_minus(i, pressure_3_sensor_list),
            get_value_or_minus(i, pressure_3_sensor_list),

            get_time_or_minus(i, pressure_4_sensor_list),
            get_value_or_minus(i, pressure_4_sensor_list),

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
                ]
            )

        time += 5
    log_file.close()