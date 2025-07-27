import sys
import queue
from queue import Queue

from time import sleep
from threading import Thread, Event
from control.controller import Controller
from gui.main_window import NewMainWindow
from PySide6.QtWidgets import QApplication
from random import randint


def start_data_handling(pressure_1_sensor_queue: Queue, pressure_2_sensor_queue: Queue,
                        pressure_3_sensor_queue: Queue,  pressure_4_sensor_queue: Queue,
                        thermocouples_1_sensor_queue: Queue, thermocouples_2_sensor_queue: Queue,
                        load_cell_1_sensor_queue: Queue,  load_cell_2_sensor_queue: Queue,
                        differential_sensor_queue: Queue, thread_killer, controller:Controller):
    """
    This function starts the data handling process.
    """
    while not thread_killer.is_set():
        pressure_1_sensor_queue.put(controller.read_pressure_1())
        pressure_2_sensor_queue.put(controller.read_pressure_2())
        pressure_3_sensor_queue.put(controller.read_pressure_3())
        pressure_4_sensor_queue.put(controller.read_pressure_4())

        thermocouples_1_sensor_queue.put(controller.read_temperature_1())
        thermocouples_2_sensor_queue.put(controller.read_temperature_2())

        load_cell_1_sensor_queue.put(controller.read_load_cell_1())
        load_cell_2_sensor_queue.put(controller.read_load_cell_2())

        differential_sensor_queue.put(controller.read_differential_pressure())

        sleep(1) # @TODO how long should we wait?

    print("Exiting data handling thread")


if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    thread_killer = Event()
    pressure_1_sensor_queue = queue.Queue()
    pressure_2_sensor_queue = queue.Queue()
    pressure_3_sensor_queue = queue.Queue()
    pressure_4_sensor_queue = queue.Queue()

    temperature_1_sensor_queue = queue.Queue()
    temperature_2_sensor_queue = queue.Queue()

    load_cell_1_sensor_queue = queue.Queue()
    load_cell_2_sensor_queue = queue.Queue()
    differential_pressure_queue = queue.Queue()

    event_queue = queue.Queue()

    # start multithreaded environment to separate UI from data handling

    controller = Controller(event_queue, thread_killer)

    data_handling_thread = Thread(target=start_data_handling,
                                  args=(pressure_1_sensor_queue,
                                        pressure_2_sensor_queue,
                                        pressure_3_sensor_queue,
                                        pressure_4_sensor_queue,

                                        temperature_1_sensor_queue,
                                        temperature_2_sensor_queue,
                                        load_cell_1_sensor_queue,
                                        load_cell_2_sensor_queue,
                                        differential_pressure_queue,
                                        thread_killer,
                                        controller))



    data_handling_thread.start()

    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(pressure_1_sensor_queue,
                                pressure_2_sensor_queue,
                                pressure_3_sensor_queue,
                                pressure_4_sensor_queue,
                                temperature_1_sensor_queue,
                                temperature_2_sensor_queue,
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
