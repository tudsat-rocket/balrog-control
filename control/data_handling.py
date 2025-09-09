import os
from datetime import datetime
import csv
from shared.shared_lists import *


class DataHandler:
    """
    Aggregate and store measurement data 
    """
    def __init__(self):
        self.writer = self.create_file(self)
        self.write_header()

    @staticmethod
    def get_value_or_minus(list):
        index = len(list[0])-1
        if index >= len(list[1]) or index < 0:
            return [-1, 1]
        else:
            return list[1][index]

    @staticmethod
    def get_time_or_minus(list):
        index = len(list[0])-1
        if index >= len(list[0]) or index < 0:
            return [-1, 1]
        else:
            return list[0][index]

    @staticmethod
    def create_file(self):
        """
        create a new log file
        """
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
        """
        write the header file for the csv
        """
        self.writer.writerow(
            ["Time pressure 0", "Pressure 0",
             "Time pressure 1", "Pressure 1",
             "Time pressure 2", "Pressure 2",
             "Time temperature Nitrous", "Temperatur Nitrous",
             "Time Engine", "Temperatur Engine",
             "Time load cell", "Thrust load cell",
             "Time Nitrous load cell", "Nitrous load cell",
             "Time Differential", "Differential Nitrous pressure",
             "Time N2OMainValve", "N2OValveState",
             "Time N2OFillValve", "N2OFillValveState",
             "Time N2OVentValve", "N2OVentValveState",
             "Time N2PurgeValve", "N2PurgeValveState",
             "TIme N2PressureValve", "N2PressureValveState"
             ]
        )

    def save(self):
        """
        save a new data point in the csv
        """
        self.writer.writerow(
            [
                self.get_time_or_minus(pressure_0_sensor_list),
                self.get_value_or_minus(pressure_0_sensor_list),

                self.get_time_or_minus(pressure_1_sensor_list),
                self.get_value_or_minus(pressure_1_sensor_list),

                self.get_time_or_minus(pressure_2_sensor_list),
                self.get_value_or_minus(pressure_2_sensor_list),

                self.get_time_or_minus(pressure_2_sensor_list),
                self.get_value_or_minus(pressure_2_sensor_list),

                self.get_time_or_minus(temperature_nitrous_sensor_list),
                self.get_value_or_minus(temperature_nitrous_sensor_list),

                self.get_time_or_minus(temperature_engine_sensor_list),
                self.get_value_or_minus(temperature_engine_sensor_list),

                self.get_time_or_minus(load_cell_1_sensor_list),
                self.get_value_or_minus(load_cell_1_sensor_list),

                self.get_time_or_minus(differential_pressure_list),
                self.get_value_or_minus(differential_pressure_list),

                self.get_time_or_minus(n2o_main_valve_sensor_list),
                self.get_value_or_minus(n2o_main_valve_sensor_list),

                self.get_time_or_minus(n2o_fill_valve_sensor_list),
                self.get_value_or_minus(n2o_fill_valve_sensor_list),

                self.get_time_or_minus(n2o_vent_valve_sensor_list),
                self.get_value_or_minus(n2o_vent_valve_sensor_list),

                self.get_time_or_minus(n2_purge_valve_sensor_list),
                self.get_value_or_minus(n2_purge_valve_sensor_list),

                self.get_time_or_minus(n2o_main_valve_sensor_list),
                self.get_value_or_minus(n2o_main_valve_sensor_list),

                self.get_time_or_minus(n2_pressure_valve_sensor_list),
                self.get_value_or_minus(n2_pressure_valve_sensor_list),

        ])

    def load(self):
        raise NotImplemented
