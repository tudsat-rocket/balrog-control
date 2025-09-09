from shared.shared_lists import *


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

    # pressure
    if len(pressure_0_sensor_list) > 0:
        pressure0 = pressure_0_sensor_list[1].copy()
        self.pressure_curve_0.setData(pressure0)
        del pressure0
    if len(pressure_1_sensor_list) > 0:
        pressure1 = pressure_1_sensor_list[1].copy()
        self.pressure_curve_1.setData(pressure1)
        del pressure1
    if len(pressure_2_sensor_list) > 0:
        pressure2 = pressure_2_sensor_list[1].copy()
        self.pressure_curve_2.setData(pressure2)
        del pressure2

    if len(differential_pressure_list) > 0 :
        differential_pressure = differential_pressure_list[1].copy()
        self.differential_pressure_curve.setData(differential_pressure)
        del differential_pressure

    # temperature
    if len(temperature_engine_sensor_list) > 0:
        temperature_engine = temperature_engine_sensor_list[1].copy()
        self.thermocouple_engine_curve.setData(temperature_engine)
        del temperature_engine
    if len(temperature_nitrous_sensor_list) > 0:
        temperature_nitrous = temperature_nitrous_sensor_list[1].copy()
        self.thermocouple_nitrous_curve.setData(temperature_nitrous)
        del temperature_nitrous

    # load cell
    if len(load_cell_1_sensor_list) > 0:
        # print(load_cell_1_sensor_list[1])
        load_cell1 = load_cell_1_sensor_list[1].copy()
        self.load_cell_thrust_curve.setData(load_cell1)
        del load_cell1
    if len(load_cell_2_sensor_list):
        load_cell2 = load_cell_2_sensor_list[1].copy()
        self.load_cell_nitrous_curve.setData(load_cell2)
        del load_cell2

    view_buffer = 500

    set_x_range(view_buffer, self.plot_pressure_0, pressure_0_sensor_list)
    set_x_range(view_buffer, self.plot_pressure_1, pressure_1_sensor_list)
    set_x_range(view_buffer, self.plot_pressure_2, pressure_2_sensor_list)

    set_x_range(view_buffer, self.plot_thermocouple_engine, temperature_engine_sensor_list)
    set_x_range(view_buffer, self.plot_thermocouple_nitrous, temperature_nitrous_sensor_list)

    set_x_range(view_buffer, self.plot_load_cell_nitrous, load_cell_1_sensor_list)
    set_x_range(view_buffer, self.plot_load_cell_thrust, load_cell_2_sensor_list)

    set_x_range(view_buffer, self.plot_differential_pressure, differential_pressure_list)


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