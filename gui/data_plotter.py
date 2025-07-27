def read_sensor_values_from_queue(self):
    """
    consume the newest values from the sensor queues
    """
    # get new pressure value from queue
    self.pressure_1_data.append(self.pressure_1_sensor_queue.get())
    self.pressure_2_data.append(self.pressure_2_sensor_queue.get())
    self.pressure_3_data.append(self.pressure_3_sensor_queue.get())
    self.pressure_4_data.append(self.pressure_4_sensor_queue.get())

    self.temperature_1_data.append(self.temperature_1_sensor_queue.get())
    self.temperature_2_data.append(self.temperature_2_sensor_queue.get())

    self.load_cell_1_data.append(self.load_cell_1_sensor_queue.get())
    self.load_cell_2_data.append(self.load_cell_2_sensor_queue.get())

    self.differential_pressure_data.append(self.differential_sensor_queue.get())

def update_plots(self):
    """
    Update the plots with new sensor values
    """

    read_sensor_values_from_queue(self)

    # @TODO how to handle time?
    if self.time_data:
        self.time_data.append(self.time_data[len(self.time_data) - 1] + 1)
        # print(self.time_data)
    else:
        self.time_data.append(0)

    # max values that are shown at the same time
    view_buffer = 500
    if len(self.time_data) < 1:
        return

    # update curves
    if len(self.time_data) > 1:
        self.pressure_curve_1.setData(self.time_data, self.pressure_1_data)
        self.pressure_curve_2.setData(self.time_data, self.pressure_2_data)
        self.pressure_curve_3.setData(self.time_data, self.pressure_3_data)
        self.pressure_curve_4.setData(self.time_data, self.pressure_4_data)

        self.thermocouple_engine_curve.setData(self.time_data, self.temperature_1_data)
        self.thermocouple_nitrous_curve.setData(self.time_data, self.temperature_2_data)
        self.load_cell_thrust_curve.setData(self.time_data, self.load_cell_1_data)
        self.load_cell_nitrous_curve.setData(self.time_data, self.load_cell_2_data)

        self.differential_pressure_curve.setData(self.time_data, self.differential_pressure_data)

    if len(self.time_data) > view_buffer:
        self.plot_pressure_1.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_thermocouple_engine.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_load_cell_thrust.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_differential_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])