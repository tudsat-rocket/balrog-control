from tinkerforge.ip_connection import IPConnection 
from tinkerforge.brick_master import BrickMaster 

class BrickHandler: 
    """
    Handler for connection to Tinkeforge Bricks
    """ 
    connection = Null;
    master = Null;

    def __init__(self):
        pass 

    def start_connection(self):
        try:
            self.connection.connect()
        except Exception as e:
            raise e

    def stop_connection(self):
        try:
            self.connection.disconnect()    
        except Exception as e:
            raise e
    
    def set_conn_params(self):
        pass

