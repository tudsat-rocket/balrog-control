from tinkerforge.ip_connection import IPConnection 
from tinkerforge.brick_master import BrickMaster 

class BrickHandler: 
    """
    Handler for connection to Tinkeforge Bricks
    """ 

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.devices = {}
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

    #TODO: maintain dicitionary of mapping between device uids and device instances


