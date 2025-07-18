from control.definitions import SensorType

class Sensor:
    """
    Abstract representation of a sensor
    """

    def __init__(self, name: str = None, sensor_type: SensorType = SensorType.DUMMY,
                 uid: str = None, pin: int = None) -> None:

        # human-readable name
        self.name = name
        self.type = sensor_type
        # uid of bricklet responsible for reading the sensor
        self.br_uid = uid
        # pin for the IO bricklet. Defines at which pin the sensor is connected to. Only used for the pressure sensor
        self.pin = pin

    def set_sensor_name(self, name: str) -> None:
        self.name = name

    def get_sensor_type(self) -> SensorType:
        return self.type

    def set_sensor_type(self, sensor_type: SensorType) -> None:
        self.type = sensor_type

    def get_br_uid(self) -> str:
        return self.br_uid

    def set_br_uid(self, uid: str) -> None:
        self.br_uid = uid

    def read_sensor(self, brick) -> int:
        """
        Read sensor value from brick
        """
        match self.type:
            case SensorType.DUMMY:
                print("Reading dummy sensor")
                return 0
            case SensorType.PRESSURE:
                return self.read_pressure(brick)
            case SensorType.TEMPERATURE:
                return self.read_temperature(brick)
            case SensorType.LOAD:
                return self.read_load(brick)

    def read_pressure(self, brick) -> int:
        """
        Reads of the IO input of the IO bricklet.
        """
        return brick.set_selected_value(self.pin)

    def read_temperature(self, brick) -> int:
        return brick.get_temperature()

    def read_load(self, brick) -> int:
        return brick.get_weight()

    def calibrate_sensor(self, brick):
        match self.type:
            case SensorType.DUMMY:
                print("Calibrating dummy sensor")
            case SensorType.LOAD:
                self.calibrate_load(brick)
            case _:
                print("Calibration failed. Not implemented for this sensor type")

    def calibrate_load(self, brick) -> None:
        """
        resets the weight the zero

        the load cell brick has to calibrated with .calibrate(weight) once.
        This can also be done in the brickViewer and is therefore not implemented here.
        see: https://www.tinkerforge.com/de/doc/Software/Bricklets/LoadCellV2_Bricklet_Python.html#load-cell-v2-bricklet-python-api
        """
        brick.tare()
