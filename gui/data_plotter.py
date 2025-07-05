def read_sensor_values_from_queue(self):
    """
    consume the newest values from the sensor queues
    """
    # get new pressure value from queue
    self.pressure_data.append(self.pressure_sensor_queue.get())
    self.current_data.append(self.current_sensor_queue.get())
    self.thermocouples_data.append(self.thermocouples_sensor_queue.get())
    self.load_cell_data.append(self.load_cell_sensor_queue.get())
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
        self.pressure_curve_1.setData(self.time_data, self.pressure_data)
        self.thermocouple_curve.setData(self.time_data, self.thermocouples_data)
        self.load_cell_curve.setData(self.time_data, self.load_cell_data)
        self.current_curve.setData(self.time_data, self.current_data)
        self.differential_pressure_curve.setData(self.time_data, self.differential_pressure_data)

    if len(self.time_data) > view_buffer:
        self.plot_current.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_thermocouple.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_load_cell.setXRange(self.time_data[-view_buffer], self.time_data[-1])
        self.plot_differential_pressure.setXRange(self.time_data[-view_buffer], self.time_data[-1])