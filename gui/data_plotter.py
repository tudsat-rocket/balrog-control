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
    time = 0
    for i in range(length):
        result.append(time)
        time += 5
    return result

def update_plots(self):
    """
    Update the plots with new sensor values
    """
    #read_sensor_values_from_queue(self)

    # update curves

    # pressure
    if len(pressure_1_sensor_list) > 0:
        pressure1 = pressure_1_sensor_list.copy()
        self.pressure_curve_1.setData(create_time_list(len(pressure1)), pressure1)
        del pressure1
    if len(pressure_2_sensor_list) > 0:
        pressure2 = pressure_2_sensor_list.copy()
        self.pressure_curve_2.setData(create_time_list(len(pressure2)), pressure2)
        del pressure2
    if len(pressure_3_sensor_list) > 0:
        pressure3 = pressure_3_sensor_list.copy()
        self.pressure_curve_3.setData(create_time_list(len(pressure3)), pressure3)
        del pressure3
    if len(pressure_4_sensor_list) > 0:
        pressure4 = pressure_4_sensor_list.copy()
        self.pressure_curve_4.setData(create_time_list(len(pressure4)), pressure4)
        del pressure4

    # temperature
    if len(temperature_engine_sensor_list) > 0:
        temperature_engine = temperature_engine_sensor_list.copy()
        self.thermocouple_engine_curve.setData(create_time_list(len(temperature_engine)), temperature_engine)
        del temperature_engine
    if len(temperature_nitrous_sensor_list) > 0:
        temperature_nitrous = temperature_nitrous_sensor_list.copy()
        self.thermocouple_nitrous_curve.setData(create_time_list(len(temperature_nitrous)), temperature_nitrous)
        del temperature_nitrous

    # load cell
    if len(load_cell_1_sensor_list) > 0:
        load_cell1 = load_cell_1_sensor_list.copy()
        self.load_cell_thrust_curve.setData(create_time_list(len(load_cell1)), load_cell1)
        del load_cell1
    if len(load_cell_2_sensor_list):
        load_cell2 = load_cell_2_sensor_list.copy()
        self.load_cell_nitrous_curve.setData(create_time_list(len(load_cell2)), load_cell2)
        del load_cell2

    if len(differential_pressure_list) > 0 :
        differential_pressure = differential_pressure_list.copy()
        self.differential_pressure_curve.setData(create_time_list(len(differential_pressure)), differential_pressure)
        del differential_pressure

    """
    if len(self.time_data) > view_buffer:
        # @TODO this is an issue now, we need to chnage that
        self.plot_pressure_1.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_thermocouple_engine.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_load_cell_thrust.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_differential_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])
    """