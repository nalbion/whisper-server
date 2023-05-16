import logging
import sys


def not_started(name: str):
    # return lambda: print(f"{name} not started")
    async def print_not_started():
        # print(f"{name} was not started")
        pass

    return print_not_started


logger = logging.getLogger("whisper_server")


def configure_logging(level: str):
    if level == "error":
        logging.basicConfig(level=logging.ERROR)
    elif level == "warning":
        logging.basicConfig(level=logging.WARNING)
    elif level == "info":
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.basicConfig(level=logging.INFO, handlers=[handler])
    elif level == "debug":
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# def signal_handler(signum: int, frame):  # FrameType | None):
#     print("signal_handler stopping mic")
#     # mic.stop()
#     print("whisper_server process terminated")
#
#
# signal.signal(signal.SIGTERM, signal_handler)
