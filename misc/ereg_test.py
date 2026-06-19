HOST = "10.42.0.81"
PORT = 4223
UID = "2552" # Change XYZ to the UID of your CAN Bricklet 2.0

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_can_v2 import BrickletCANV2


def parse_can_adc(can_data: tuple) -> int:
    conversion_result = int.from_bytes(bytes(can_data), byteorder='little')
    return conversion_result

def cb_frame_read(frame_type, identifier, data):
    count_adc = parse_can_adc(data)
    v_adc = parse_can_adc(data) / 1024 * 3.3

    # Kalibrierung Mit was regeln?


if __name__ == "__main__":

    ipcon = IPConnection()
    can = BrickletCANV2(UID, ipcon)
    ipcon.connect(HOST, PORT)
    can.set_transceiver_configuration(125000, 875, can.TRANSCEIVER_MODE_NORMAL)
    can.register_callback(can.CALLBACK_FRAME_READ, cb_frame_read)
    can.set_frame_read_callback_configuration(True)
    input("Press key to exit\n")
    can.set_frame_read_callback_configuration(False)
    ipcon.disconnect()