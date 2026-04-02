from collections.abc import Callable

from control.definitions import SensorType


class Sensor:
    """Abstract representation of a sensor"""

    def __init__(
        self,
        name: str = None,
        sensor_type: SensorType = SensorType.DUMMY,
        uid: str = None,
        channel: int = None,
        callback: Callable = None,
        period: int = 1000,
    ) -> None:
        """Construct a new sensor object.

        This creates a new sensor object. This can represent different
        sensors like pressure, load or temperature.
        @callback: The callback function that will be
        called when the sensor has a new value
        @period: The period of the sensor callback, in ms. Default is 1000ms = 1s
        """
        # human-readable name
        self.name: str = name
        self.type: SensorType = sensor_type
        # uid of bricklet responsible for reading the sensor
        self.br_uid = uid
        # channel for the industrial dual bricklet. Only used for the pressure sensor
        self.channel = channel
        self.callback = callback
        self.period = period

    def get_sensor_type(self) -> SensorType:
        return self.type

    def set_sensor_type(self, sensor_type: SensorType) -> None:
        self.type = sensor_type

    def get_br_uid(self) -> str:
        return self.br_uid

    def set_br_uid(self, uid: str) -> None:
        self.br_uid = uid

    def calibrate_sensor(self, brick) -> None:
        """Calibrate the sensor.

        This is currently only supported for the load cell sensor.
        Other sensor won't be calibrated.
        """
        match self.type:
            case SensorType.DUMMY:
                print("Calibrating dummy sensor")
            case SensorType.LOAD:
                self.calibrate_load(brick)
            case _:
                print("Calibration failed. Not implemented for this sensor type")

    def calibrate_load(self, brick, weight=None) -> None:
        """Resets the weight to zero.

        The load cell brick has to calibrated with .calibrate(weight) once.
        This can also be done in the brickViewer and is therefore not implemented here.
        see: https://www.tinkerforge.com/de/doc/Software/Bricklets/LoadCellV2_Bricklet_Python.html#load-cell-v2-bricklet-python-api
        """
        if weight is not None:
            brick.calibrate(weight)
        else:
            brick.tare()

    def enable_callback(self, brick):
        """Activates/enables the callbacks for new sensor values.

        This starts the recording of new sensor values.
        """
        self._setup_callback(brick)
        match self.type:
            case SensorType.TEMPERATURE:
                # parameters are period in ms, value_has_to_change,
                # Threshold (x =disabled), min, max
                brick.set_temperature_callback_configuration(
                    self.period, False, "x", 0, 0
                )
            case SensorType.PRESSURE:
                # parameters are: channel, period in ms, threshold, min, max
                brick.set_sample_rate(3)
                brick.set_current_callback_configuration(
                    self.channel, self.period, False, "x", 0, 0
                )
            case SensorType.LOAD:
                brick.set_weight_callback_configuration(self.period, False, "x", 0, 0)
            case SensorType.SERVO_STATE:
                brick.set_position_reached_callback_configuration(self.channel, False)

    def disable_callback(self, brick):
        """Disable the sensor callback functions.

        This stops the recording of sensor values.
        To restart the sensor, call enable_callback again.
        @TODO(Nucleus): Move to smaller method with correct type annotation
        """
        #  period of 0 disables the callback
        match self.type:
            case SensorType.TEMPERATURE:
                brick.set_temperature_callback_configuration(0, False, "x", 0, 0)
            case SensorType.PRESSURE:
                brick.set_current_callback_configuration(
                    self.channel, 0, False, "x", 0, 0
                )
            case SensorType.LOAD:
                brick.set_weight_callback_configuration(0, False, "x", 0, 0)
            case SensorType.SERVO_STATE:
                brick.set_position_reached_callback_configuration(self.channel, False)

    def read_sensor(self, brick) -> int:
        """Read sensor value from brick.

        Currently, this is not used, as we are using the callbacks instead.
        """
        match self.type:
            case SensorType.DUMMY:
                return 0
            case SensorType.PRESSURE:
                return self._read_pressure(brick)
            case SensorType.TEMPERATURE:
                return self._read_temperature(brick)
            case SensorType.LOAD:
                return self._read_load(brick)
            case SensorType.DIFFERENTIAL_PRESSURE:
                return self._read_pressure(brick)
            case SensorType.SERVO_STATE:
                return self._read_servo_state(brick)

    def _read_servo_state(self, brick) -> int:
        return brick.get_current_position(self.channel)

    def _read_pressure(self, brick) -> int:
        """Read the pressure value
        Reads of the IO input of the industrial dual bricklet.
        @TODO(Nucleus): We could display an warning,
         if we expect that the sensor is either broken or not connected
        """
        print("read pressure")
        current = brick.get_current(self.channel)
        if current < 4:
            # there is no sensor connected!
            pass
        if current > 20:
            # the sensor has a malfunction, Please check the sensor
            pass
        return current

    def _read_temperature(self, brick) -> int:
        temperature = brick.get_temperature()
        print(temperature)
        return temperature

    def _read_load(self, brick) -> int:
        weight = brick.get_weight()
        return weight

    def _setup_callback(self, brick) -> None:
        """Connects our callbacks to the sensor callbacks.

        This registers the callback stored in self.callback with the tinkerforge brick.
        """
        match self.type:
            case SensorType.TEMPERATURE:
                brick.register_callback(brick.CALLBACK_TEMPERATURE, self.callback)
            case SensorType.PRESSURE:
                brick.register_callback(brick.CALLBACK_CURRENT, self.callback)
            case SensorType.LOAD:
                brick.register_callback(brick.CALLBACK_WEIGHT, self.callback)
            case SensorType.SERVO_STATE:
                brick.register_callback(brick.CALLBACK_POSITION_REACHED, self.callback)
