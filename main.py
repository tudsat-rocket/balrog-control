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



if __name__ == "__main__":
    # define shared queue between threads to communicate sensor values
    thread_killer = Event()

    event_queue = queue.Queue()

    # start multithreaded environment to separate UI from data handling

    controller = Controller(event_queue, thread_killer)


    """
    Start the main UI window
    """
    app = QApplication(sys.argv)
    main_window = NewMainWindow(event_queue, controller)
    main_window.show()
    rc = app.exec()


    # join the threads again
    thread_killer.set()
    #data_handling_thread.join(timeout=5)
    sys.exit(rc)
