from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_industrial_dual_0_20ma_v2 import BrickletIndustrialDual020mAV2
from tinkerforge.bricklet_industrial_dual_ac_relay import BrickletIndustrialDualACRelay
from tinkerforge.bricklet_io16_v2 import BrickletIO16V2
from tinkerforge.bricklet_load_cell_v2 import BrickletLoadCellV2
from tinkerforge.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from tinkerforge.bricklet_servo_v2 import BrickletServoV2
from tinkerforge.bricklet_thermocouple_v2 import BrickletThermocoupleV2
from tinkerforge.ip_connection import Device as tk_device
from tinkerforge.ip_connection import Error, IPConnection


class StackHandler:
    """Handler for connection to a Stack of TinkeForge Bricks and attached Bricklets."""

    def __init__(self, devices: dict = {}):
        self.devices: dict = devices
        self.connection: IPConnection = IPConnection()

    def start_connection(self, host: str, port: int = 4223) -> None:
        """Create a new connection to the thnkerforge stack.

        This connects with the given hostname and port to the thinkerforge stack.
        Raises: an Exception if the connection failed.
        """
        try:
            self.connection.connect(host, port)
            self.connection.register_callback(
                IPConnection.CALLBACK_ENUMERATE,
                self.cb_enumerate
            )
            self.connection.enumerate()
        except Error as err:
            raise err

    def stop_connection(self) -> None:
        """End the connection to the thinkerforge stack.

        This closes the connection to allow reconnecting.
        Raises: An Exception if the disconnect failed.
        """
        try:
            self.connection.disconnect()
        except Error as err:
            raise err

    def add_device(self, uid: str, device_type: int) -> None:
        """Add new device to device stack.

        This takes the UID and the type of the device and creates a device from that.
        Raises: An Exception if device could not be added.
        """
        print(f"Add device with UID {uid}")
        try:
            self.devices[uid] = self._construct_from_device_type(device_type, uid)
        except RuntimeError as err:
            raise err

    def get_device(self, uid: str) -> tk_device:
        try:
            return self.devices[uid]
        except KeyError as err:
            raise err

    def cb_enumerate(
        self,
        uid,
        connected_uid,
        position,
        hardware_version,
        firmware_version,
        device_identifier,
        enumeration_type,
    ) -> None:
        if (
            enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE
        ):  # @TODO fix: or IPConnection.ENUMERATION_TYPE_CONNECTED:
            # construct device based on device device_identifier
            print(f"enumerate {uid}")
            self.add_device(uid, device_identifier)

    # Internal
    def _construct_from_device_type(
        self, device_type: int, uid: str
    ) -> tk_device | None:
        match device_type:
            case 13:
                return BrickMaster(uid, self.connection)
            case 2120:
                return BrickletIndustrialDual020mAV2(uid, self.connection)
            case 2104:
                return BrickletLoadCellV2(uid, self.connection)
            case 2109:
                return BrickletThermocoupleV2(uid, self.connection)
            case 2114:
                return BrickletIO16V2(uid, self.connection)
            case 2137:
                return BrickletSegmentDisplay4x7V2(uid, self.connection)
            case 2157:
                return BrickletServoV2(uid, self.connection)
            case 2162:
                return BrickletIndustrialDualACRelay(uid, self.connection)
            case 2107:
                pass
            case _:
                raise RuntimeError(f"Unknown device type {device_type}")
