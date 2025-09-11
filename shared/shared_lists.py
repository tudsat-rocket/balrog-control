import yaml

# pressure
pressure_0_sensor_list = [[],[]]
pressure_1_sensor_list = [[],[]]
pressure_2_sensor_list = [[],[]]
pressure_3_sensor_list = [[],[]]
differential_pressure_list = [[],[]]

# temp
temperature_nitrous_sensor_list = [[],[]]
temperature_engine_sensor_list = [[],[]]

# load cell
load_cell_1_sensor_list = [[],[]]
load_cell_2_sensor_list = [[],[]]

#servo
n2o_main_valve_sensor_list = [[],[]]
n2o_fill_valve_sensor_list = [[],[]]
n2o_vent_valve_sensor_list = [[],[]]
n2_pressure_valve_sensor_list = [[],[]]
n2_purge_valve_sensor_list = [[],[]]

n2o_qd_state_list = [[],[]]


balrog_cfg = None
with open('config/balrog.yaml', 'r') as f:
    balrog_cfg = yaml.load(f, Loader=yaml.SafeLoader)
    actors_dict = {}
    for actor in balrog_cfg["actors"]:
        actors_dict[actor["name"]] = actor
    balrog_cfg["actors"] = actors_dict