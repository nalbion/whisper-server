

def not_started(name: str):
    # return lambda: print(f"{name} not started")
    async def print_not_started():
        # print(f"{name} was not started")
        pass

    return print_not_started

# def signal_handler(signum: int, frame):  # FrameType | None):
#     print("signal_handler stopping mic")
#     # mic.stop()
#     print("whisper_server process terminated")
#
#
# signal.signal(signal.SIGTERM, signal_handler)
