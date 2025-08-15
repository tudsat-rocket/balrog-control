import queue

pressure_1_sensor_queue = queue.Queue()
pressure_2_sensor_queue = queue.Queue()
pressure_3_sensor_queue = queue.Queue()
pressure_4_sensor_queue = queue.Queue()

temperature_nitrous_sensor_queue = queue.Queue()
temperature_engine_sensor_queue = queue.Queue()

load_cell_1_sensor_queue = queue.Queue()
load_cell_2_sensor_queue = queue.Queue()
differential_pressure_queue = queue.Queue()


pressure_1_sensor_list = []
pressure_2_sensor_list = []
pressure_3_sensor_list = []
pressure_4_sensor_list = []

temperature_nitrous_sensor_list = []
temperature_engine_sensor_list = []

load_cell_1_sensor_list = []
load_cell_2_sensor_list = []
differential_pressure_list = []