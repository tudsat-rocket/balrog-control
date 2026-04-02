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


class DataHandler:
    """Aggregate and store measurement data"""

    def __init__(self):
        self.writer = self.create_file(self)
        self.write_header()

    @staticmethod
    def get_value_or_minus(list):
        index = len(list[0]) - 1
        if index >= len(list[1]) or index < 0:
            return [-1, 1]
        else:
            return list[1][index]

    @staticmethod
    def get_time_or_minus(list):
        index = len(list[0]) - 1
        if index >= len(list[0]) or index < 0:
            return [-1, 1]
        else:
            return list[0][index]

    @staticmethod
    def create_file(self):
        """Create a new log file"""
        print("create file for log")
        # create log folder if not exists
        if not os.path.exists("logs"):
            os.makedirs("logs")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        current_log_filename = f"log_{timestamp}.csv"
        filepath = os.path.join("logs", current_log_filename)
        log_file = open(filepath, "w", newline="")
        return csv.writer(log_file)

    def write_header(self):
        """Write the header file for the csv"""
        self.writer.writerow(
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

    def save(self):
        """Save a new data point in the csv"""
        self.writer.writerow(
            [
                self.get_time_or_minus(pressure_0_sensor_list),
                self.get_value_or_minus(pressure_0_sensor_list),
                self.get_time_or_minus(pressure_1_sensor_list),
                self.get_value_or_minus(pressure_1_sensor_list),
                self.get_time_or_minus(pressure_2_sensor_list),
                self.get_value_or_minus(pressure_2_sensor_list),
                self.get_time_or_minus(temperature_ox_sensor_list),
                self.get_value_or_minus(temperature_ox_sensor_list),
                self.get_time_or_minus(temperature_engine_sensor_list),
                self.get_value_or_minus(temperature_engine_sensor_list),
                self.get_time_or_minus(load_cell_thrust_sensor_list),
                self.get_value_or_minus(load_cell_thrust_sensor_list),
                self.get_time_or_minus(load_cell_ox_sensor_list),
                self.get_value_or_minus(load_cell_ox_sensor_list),
                self.get_time_or_minus(cc_pressure_0_sensor_list),
                self.get_value_or_minus(cc_pressure_0_sensor_list),
                self.get_time_or_minus(cc_pressure_1_sensor_list),
                self.get_value_or_minus(cc_pressure_1_sensor_list),
                self.get_time_or_minus(main_valve_sensor_list),
                self.get_value_or_minus(main_valve_sensor_list),
                self.get_time_or_minus(fill_valve_sensor_list),
                self.get_value_or_minus(fill_valve_sensor_list),
                self.get_time_or_minus(vent_valve_sensor_list),
                self.get_value_or_minus(vent_valve_sensor_list),
                self.get_time_or_minus(purge_valve_sensor_list),
                self.get_value_or_minus(purge_valve_sensor_list),
                self.get_time_or_minus(pressurization_valve_sensor_list),
                self.get_value_or_minus(pressurization_valve_sensor_list),
            ]
        )

    def load(self):
        raise NotImplementedError
