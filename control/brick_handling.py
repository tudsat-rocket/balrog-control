from tinkerforge.ip_connection import IPConnection, Error 
from tinkerforge.brick_master import BrickMaster 
from tinkerforge.bricklet_servo_v2 import BrickletServoV2
from tinkerforge.bricklet_thermocouple_v2 import BrickletThermocoupleV2
from tinkerforge.bricklet_load_cell_v2 import BrickletLoadCellV2
from tinkerforge.bricklet_segment_display_4x7_v2 import BrickletSegmentDisplay4x7V2
from tinkerforge.bricklet_industrial_dual_ac_relay import BrickletIndustrialDualACRelay
from tinkerforge.bricklet_io16_v2 import BrickletIO16V2
from tinkerforge.bricklet_industrial_dual_0_20ma_v2 import BrickletIndustrialDual020mAV2

class StackHandler: 
    """
    Handler for connection to a Stack of TinkeForge Bricks and attached Bricklets
    """ 

    def __init__(self, host: str = "localhost", port: int = 4223, devices = {}):
        self.host = host
        self.port = port
        self.devices = devices
        self.connection = IPConnection()
        pass 


    def start_connection(self) -> None:
        try:
            self.connection.connect(self.host, self.port)
        except Exception as err:
            raise err


    def stop_connection(self) -> None:
        try:
            self.connection.disconnect()    
        except Exception as err:
            raise err


    def set_conn_params(self, host, port) -> None:
        self.host = host 
        self.port = port 


    def add_device(self, uid: str, device_type) -> None:
        pass

    
    def cb_enumerate(self, uid, connected_uid, position, hardware_version, 
                     firmware_version, device_identifier, enumeration_type) -> None:

        if enumeration_type == IPConnection.AVAILABLE:
            
            device = None # construct device based on device device_identifier
            self.devices[uid] = device 

        #TODO: (semi done) maintain dicitionary of mapping between device uids and device instances
        

