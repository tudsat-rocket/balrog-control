import queue
from shared.shared_queues import *

def read_sensor_values_from_queue(self) -> bool:
    """
    consume the newest values from the sensor queues
    returns False if there are no new values
    """
    # get new pressure value from queue
    try:
        self.pressure_1_data.append(pressure_1_sensor_queue.get(False))
    except queue.Empty:
        # print("pressure 1 is empty")
        pass
    try:
        self.pressure_2_data.append(pressure_2_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.pressure_3_data.append(pressure_3_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.pressure_4_data.append(pressure_4_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.temperature_1_data.append(temperature_nitrous_sensor_queue.get(False))
    except queue.Empty:
        # print("nitrous is empty")
        pass
    try:
        self.temperature_2_data.append(temperature_engine_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.load_cell_1_data.append(load_cell_1_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.load_cell_2_data.append(load_cell_2_sensor_queue.get(False))
    except queue.Empty:
        pass
    try:
        self.differential_pressure_data.append(differential_pressure_queue.get(False))
    except queue.Empty:
        pass

def create_time_list(length):
    result = []
    for i in range(length):
        result.append(i)
    return result

def update_plots(self):
    """
    Update the plots with new sensor values
    """
    read_sensor_values_from_queue(self)

    # update curves

    # pressure
    if len(self.pressure_1_data) > 0:
        self.pressure_curve_1.setData(create_time_list(len(self.pressure_1_data)), self.pressure_1_data)
    if len(self.pressure_2_data) > 0:
        self.pressure_curve_2.setData(create_time_list(len(self.pressure_2_data)), self.pressure_2_data)
    if len(self.pressure_3_data) > 0:
        self.pressure_curve_3.setData(create_time_list(len(self.pressure_3_data)), self.pressure_3_data)
    if len(self.pressure_4_data) > 0:
        self.pressure_curve_4.setData(create_time_list(len(self.pressure_4_data)), self.pressure_4_data)

    # temperature
    if len(self.temperature_1_data) > 0:
        self.thermocouple_engine_curve.setData(create_time_list(len(self.temperature_1_data)), self.temperature_1_data)
    if len(self.temperature_2_data) > 0:
        self.thermocouple_nitrous_curve.setData(create_time_list(len(self.temperature_2_data)), self.temperature_2_data)

    # load cell
    if len(self.load_cell_1_data) > 0:
        self.load_cell_thrust_curve.setData(create_time_list(len(self.load_cell_1_data)), self.load_cell_1_data)
    if len(self.differential_pressure_data):
        self.load_cell_nitrous_curve.setData(create_time_list(len(self.load_cell_2_data)), self.load_cell_2_data)
    if len(self.differential_pressure_data) > 0 :
        self.differential_pressure_curve.setData(create_time_list(len(self.differential_pressure_data)), self.differential_pressure_data)

    """
    if len(self.time_data) > view_buffer:
        # @TODO this is an issue now, we need to chnage that
        self.plot_pressure_1.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_thermocouple_engine.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_load_cell_thrust.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_differential_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])
    """