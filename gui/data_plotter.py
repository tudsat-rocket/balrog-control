from shared.shared_lists import *
from datetime import datetime

t0 = datetime.now()

def create_time_list(length):
    result = []
    time = 0
    for i in range(length):
        result.append(time)
        time += 5
    return result

def set_x_range(view_buffer, plot, data_list):
    if len(data_list[0]) > view_buffer:
        plot.setAutoPan(x=True) # this allows a smooth pan, while you still can manually scroll
        plot.setAutoVisible(y=True)
        #plot.setXRange(len(data_list[0]) - view_buffer, len(data_list[0]) - 1)


def update_plots(self):
    """
    Update the plots with new sensor values
    """
    #read_sensor_values_from_queue(self)

    # update curves
    #print(pressure_2_sensor_list)

    
    max_time = \
        max([
            (pressure_0_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(pressure_0_sensor_list[0]) > 0 else float("-inf"),
            (pressure_1_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(pressure_1_sensor_list[0]) > 0 else float("-inf"),
            (pressure_2_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(pressure_2_sensor_list[0]) > 0 else float("-inf"),
            (differential_pressure_list[0][-1] - self.controller.t0).total_seconds() if len(differential_pressure_list[0]) > 0 else float("-inf"),
            (temperature_engine_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(temperature_engine_sensor_list[0]) > 0 else float("-inf"),
            (temperature_nitrous_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(temperature_nitrous_sensor_list[0]) > 0 else float("-inf"),
            (load_cell_1_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(load_cell_1_sensor_list[0]) > 0 else float("-inf"),
            (load_cell_2_sensor_list[0][-1] - self.controller.t0).total_seconds() if len(load_cell_2_sensor_list[0]) > 0 else float("-inf"),
        ])

    def get_time(timestamps):
        return [(i - self.controller.t0).total_seconds() for i in timestamps].copy()

    def pan_to_current(curve):
        window = 60 #seconds
        curve.setXRange(max(0, max_time - window), max_time)

    # pressure
    if len(pressure_0_sensor_list[0]) > 0:
        self.current_value_n2_tank.setText("{:.3f}".format(pressure_0_sensor_list[1][-1]))
        pressure0 = pressure_0_sensor_list[1][len(pressure_0_sensor_list[1]) - 500:].copy()
        self.pressure_curve_0.setData(get_time(pressure_0_sensor_list[0]), pressure0)
        pan_to_current(self.plot_pressure_0)
        del pressure0
    if len(pressure_1_sensor_list[0]) > 0:
        self.current_value_n2o_tank.setText("{:.3f}".format(pressure_1_sensor_list[1][-1]))
        pressure1 = pressure_1_sensor_list[1].copy()
        self.pressure_curve_1.setData(get_time(pressure_1_sensor_list[0]), pressure1)
        pan_to_current(self.plot_pressure_1)
        del pressure1
    if len(pressure_2_sensor_list[0]) > 0:
        self.current_value_pre_chamber_pressure.setText("{:.3f}".format(pressure_2_sensor_list[1][-1]))
        pressure2 = pressure_2_sensor_list[1].copy()
        self.pressure_curve_2.setData(get_time(pressure_2_sensor_list[0]), pressure2)
        pan_to_current(self.plot_pressure_2)
        del pressure2

    if len(differential_pressure_list[0]) > 0 :
        self.current_value_differential_pressure.setText("{:.3f}".format(differential_pressure_list[1][-1]))
        differential_pressure = differential_pressure_list[1].copy()
        self.differential_pressure_curve.setData(get_time(differential_pressure_list[0]), differential_pressure)
        pan_to_current(self.plot_differential_pressure)
        del differential_pressure

    # temperature
    if len(temperature_engine_sensor_list[0]) > 0:
        self.current_value_temperature_engine.setText("{:.3f}".format(temperature_engine_sensor_list[1][-1]))
        temperature_engine = temperature_engine_sensor_list[1].copy()#[len(temperature_engine_sensor_list[1]) - 500:].copy()
        self.thermocouple_engine_curve.setData(get_time(temperature_engine_sensor_list[0]), temperature_engine)
        pan_to_current(self.plot_thermocouple_engine)
        del temperature_engine
    if len(temperature_nitrous_sensor_list[0]) > 0:
        self.current_value_temperature_nitrous.setText("{:.3f}".format(temperature_nitrous_sensor_list[1][-1]))
        temperature_nitrous = temperature_nitrous_sensor_list[1].copy()
        self.thermocouple_nitrous_curve.setData(get_time(temperature_nitrous_sensor_list[0]), temperature_nitrous)
        pan_to_current(self.plot_thermocouple_nitrous)
        del temperature_nitrous

    # load cell
    if len(load_cell_1_sensor_list[0]) > 0:
        self.current_value_load_cell_thrust.setText("{:.3f}".format(load_cell_1_sensor_list[1][-1]))
        load_cell1 = load_cell_1_sensor_list[1].copy()
        self.load_cell_thrust_curve.setData(get_time(load_cell_1_sensor_list[0]), load_cell1)
        pan_to_current(self.plot_load_cell_thrust)
        del load_cell1
    if len(load_cell_2_sensor_list[0]):
        self.current_value_load_cell_nitrous.setText("{:.3f}".format(load_cell_2_sensor_list[1][-1]))
        load_cell2 = load_cell_2_sensor_list[1].copy()
        self.load_cell_nitrous_curve.setData(get_time(load_cell_2_sensor_list[0]), load_cell2)
        pan_to_current(self.plot_load_cell_nitrous)
        del load_cell2

    # view_buffer = 500

    # set_x_range(view_buffer, self.plot_pressure_0, pressure_0_sensor_list)
    # set_x_range(view_buffer, self.plot_pressure_1, pressure_1_sensor_list)
    # set_x_range(view_buffer, self.plot_pressure_2, pressure_2_sensor_list)

    # set_x_range(view_buffer, self.plot_thermocouple_engine, temperature_engine_sensor_list)
    # set_x_range(view_buffer, self.plot_thermocouple_nitrous, temperature_nitrous_sensor_list)

    # set_x_range(view_buffer, self.plot_load_cell_nitrous, load_cell_1_sensor_list)
    # set_x_range(view_buffer, self.plot_load_cell_thrust, load_cell_2_sensor_list)

    # set_x_range(view_buffer, self.plot_differential_pressure, differential_pressure_list)


    """if len(pressure_0_sensor_list[0]) > view_buffer:
        # @TODO this is an issue now, we need to change that
        self.plot_pressure_0.setXRange(len(pressure_0_sensor_list[0])-view_buffer, len(pressure_0_sensor_list[0])-1)
        #self.plot_pressure_1.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        #self.plot_pressure_2.setXRange(self.time_data[-view_buffer], self.time_data[-1])

        #self.plot_thermocouple_engine.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        #self.plot_thermocouple_nitrous.setXRange(self.time_data[-view_buffer], self.time_data[-1])

        #self.plot_load_cell_nitrous.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_load_cell_nitrous.setXRange(len(load_cell_1_sensor_list[0])-view_buffer, len(load_cell_1_sensor_list[0])-1)
        self.plot_load_cell_thrust.setXRange(len(load_cell_2_sensor_list[0])-view_buffer, len(load_cell_2_sensor_list[0])-1)

        #self.plot_differential_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])
    """