import sys
import queue
from queue import Queue

from time import sleep
from threading import Thread, Event
from control.controller import Controller
from gui.main_window import NewMainWindow
from PySide6.QtWidgets import QApplication
from random import randint

# store connection state
connected = False
from shared.shared_queues import *


def start_data_handling(pressure_1_sensor_queue: Queue, pressure_2_sensor_queue: Queue,
                        pressure_3_sensor_queue: Queue,  pressure_4_sensor_queue: Queue,
                        thermocouples_1_sensor_queue: Queue, thermocouples_2_sensor_queue: Queue,
                        load_cell_1_sensor_queue: Queue,  load_cell_2_sensor_queue: Queue,
                        differential_sensor_queue: Queue, thread_killer, controller:Controller):
    """
    This function starts the data handling process.
    """
    while not thread_killer.is_set():
        """
        try:
            pressure_1_sensor_queue.put(controller.read_pressure_1())
        except Exception as e:
            print(f"Failed to read pressure 1. {e}")
        try:
            pressure_2_sensor_queue.put(controller.read_pressure_2())
        except Exception as e:
            print(f"Failed to read pressure 2. {e}")
        try:
            pressure_3_sensor_queue.put(controller.read_pressure_3())
        except Exception as e:
            print(f"Failed to read pressure 3. {e}")
        try:
            pressure_4_sensor_queue.put(controller.read_pressure_4())
        except Exception as e:
            print(f"Failed to read pressure 4. {e}")
        try:
            thermocouples_1_sensor_queue.put(controller.read_temperature_1())
        except Exception as e:
            print(f"Failed to read temperature 1. {e}")
        try:
            thermocouples_2_sensor_queue.put(controller.read_temperature_2())
        except Exception as e:
            print(f"Failed to read temperature 2. {e}")
        try:
            load_cell_1_sensor_queue.put(controller.read_load_cell_1())
        except Exception as e:
            print(f"Failed to read load cell 1. {e}")
        try:
            load_cell_2_sensor_queue.put(controller.read_load_cell_2())
        except Exception as e:
            print(f"Failed to read load cell 2. {e}")
        try:
            differential_sensor_queue.put(controller.read_differential_pressure())
        except Exception as e:
            print(f"Failed to read differential pressure. {e}")

        sleep(1) # @TODO how long should we wait?
    """
    print("Exiting data handling thread")


if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    thread_killer = Event()

    event_queue = queue.Queue()

    # start multithreaded environment to separate UI from data handling

    controller = Controller(event_queue)

    data_handling_thread = Thread(target=start_data_handling,
                                  args=(pressure_1_sensor_queue,
                                        pressure_2_sensor_queue,
                                        pressure_3_sensor_queue,
                                        pressure_4_sensor_queue,

                                        temperature_nitrous_sensor_queue,
                                        temperature_engine_sensor_queue,
                                        load_cell_1_sensor_queue,
                                        load_cell_2_sensor_queue,
                                        differential_pressure_queue,
                                        thread_killer,
                                        controller))


    # the data handler is not needed anymore as we are using the callbacks for the sensor values now
    # data_handling_thread.start()

    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(pressure_1_sensor_queue,
                                pressure_2_sensor_queue,
                                pressure_3_sensor_queue,
                                pressure_4_sensor_queue,
                                temperature_nitrous_sensor_queue,
                                temperature_engine_sensor_queue,
                                load_cell_1_sensor_queue,
                                load_cell_2_sensor_queue,
                                differential_pressure_queue,
                                event_queue, controller)
    main_window.show()
    rc = app.exec()


    # join the threads again
    thread_killer.set()
    data_handling_thread.join(timeout=5)
    sys.exit(rc)
