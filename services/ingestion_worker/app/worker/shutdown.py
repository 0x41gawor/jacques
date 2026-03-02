import signal
import threading

shutdown_event = threading.Event()

def signal_handler(signum, frame):
    shutdown_event.set()

def register_signal_handlers():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)