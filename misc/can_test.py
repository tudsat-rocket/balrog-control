HOST = "10.42.0.81"
PORT = 4223
UID = "2552" # Change XYZ to the UID of your CAN Bricklet 2.0

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_can_v2 import BrickletCANV2


def parse_can_adc(can_data: tuple) -> int:
    """
    Parses 2 bytes of CAN data from little-endian to an integer.

    Args:
        can_data (tuple): A tuple containing 2 bytes, e.g., (78, 0)

    Returns:
        int: The 10-bit ADC conversion result.
    """
    # Convert tuple to bytes and parse as little-endian unsigned 16-bit integer
    conversion_result = int.from_bytes(bytes(can_data), byteorder='little')

    # Note: The sender already masked and shifted the value:
    # ((conversion_register >> 2) & 0x3ff)
    # So conversion_result is directly your 10-bit ADC value (0 - 1023)
    return conversion_result

def cb_frame_read(frame_type, identifier, data):
    #if frame_type == BrickletCANV2.FRAME_TYPE_STANDARD_DATA:
    #    print("Frame Type: Standard Data")
    #elif frame_type == BrickletCANV2.FRAME_TYPE_STANDARD_REMOTE:
    #    print("Frame Type: Standard Remote")
    #elif frame_type == BrickletCANV2.FRAME_TYPE_EXTENDED_DATA:
    #    print("Frame Type: Extended Data")
    #elif frame_type == BrickletCANV2.FRAME_TYPE_EXTENDED_REMOTE:
    #    print("Frame Type: Extended Remote")
    #print("Identifier: " + str(identifier))
    #print("Data (Length: " + str(len(data)) + "): " + ", ".join(map(str, data[:min(len(data), 8)])))
    #print(data)
    #if str(identifier) == "191":
    if identifier < 200:
        binary_data = " ".join(f"{b:08b}" for b in data)
        print(str(identifier) + "   -   " + str(parse_can_adc(data) / 1024 * 3.3) + "   -   " + str(data) + "   -   " + str(parse_can_adc(data)) + "   -   " + binary_data)
    #print(int.from_bytes(data, byteorder='little'))

    # 190 0.25xxxx
    # 191 0.0064453125
    # 1024 = 3.3V

if __name__ == "__main__":

    ipcon = IPConnection()
    can = BrickletCANV2(UID, ipcon)
    ipcon.connect(HOST, PORT)
    can.set_transceiver_configuration(125000, 875, can.TRANSCEIVER_MODE_NORMAL)
    can.register_callback(can.CALLBACK_FRAME_READ, cb_frame_read)
    can.set_frame_read_callback_configuration(True)
    input("Press key to exit\n") # Use raw_input() in Python 2
    can.set_frame_read_callback_configuration(False)
    ipcon.disconnect()