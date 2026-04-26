import time
from shared.state import telemetry_lock, telemetry, disk_queue


def to_bar_100(val): return 6.248047485 * (val / 1e6) - 24.992191
def to_bar_160(val): return 10.0 * ((val  ) / 1e6) - 40.0 #* 0.5
def to_temp_c(val): return val / 100.0
def to_kg(val): return val / 1000.0
def to_current_ma(val): return val / 1000000.0
def identity(val): return val

# TODO: Extract into config, only linear scaling
CALLBACK_CONFIG = {
    "pressure_tank":        to_bar_100,
    "pressure_ox_bottle":   to_bar_100,
    "pressure_n2_bottle":   to_bar_100,
    "pressure_cc_pre":      to_bar_100,
    "pressure_cc0":         to_bar_160,
    "pressure_cc1":         to_bar_160,
    "temp_engine":     to_temp_c,
    "temp_ox":         to_temp_c,
    "load_cell_thrust": to_kg,
    "load_cell_ox":     to_kg,
}

def create_master_callback(controller, sensor_units):
    """
    Erzeugt einen Dispatcher für ein Bricklet.
    sensor_units: Liste von Dicts [{'name':.., 'channel':..}]
    """
    dispatch_map = []
    for unit in sensor_units:
        name = unit['name']
        dispatch_map.append({
            'channel': unit['channel'],
            'name': name,
            'transform': CALLBACK_CONFIG.get(name, identity)
        })

    def master_dispatcher(*args):
        if len(args) > 1:
            incoming_chan, raw_value = args[0], args[1]
        else:
            incoming_chan, raw_value = -1, args[0]

        ts = controller.t0_wall + (time.perf_counter() - controller.t0_perf)

        # Den passenden Sensor für den eintreffenden Kanal finden
        for s in dispatch_map:
            if incoming_chan == s['channel']:
                processed = s['transform'](raw_value)

                with telemetry_lock:
                    telemetry[s['name']] = (ts, processed)
                disk_queue.put((s['name'], ts, processed))
                return

    return master_dispatcher
