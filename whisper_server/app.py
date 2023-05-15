import asyncio
from multiprocessing import Queue, Event
import queue
import signal
import sys

from whisper_server.services.audio.start_audio import start_audio_thread
from whisper_server.services.server.start_servers import start_grpc_server, start_http_server_thread
from whisper_server.services.whisper.start_whisper import start_whisper_process
from whisper_server.services.utils import not_started

async def main():
    print("whisper_server starting...")
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    audio_active_event = Event()
    interrupted_event = Event()
    audio_queue = Queue()
    stt_results_queue = Queue()
    # commands_process = multiprocessing.Process(target=command_handler)

    stop_audio = not_started("audio")
    stop_whisper = not_started("whisper")
    stop_http_server = not_started("http server")
    stop_grpc_server = not_started("grpc server")

    try:
        stop_audio = start_audio_thread(audio_queue, audio_active_event)
        stop_whisper = start_whisper_process(audio_queue, stt_results_queue, interrupted_event)
        # stop_whisper = start_whisper_thread(audio_queue, stt_results_queue)

        if False:
            audio_active_event.set()
            log_whisper(stt_results_queue)
            stop_http_server = start_http_server_thread(stt_results_queue)
        else:
            stop_grpc_server = start_grpc_server(stt_results_queue, audio_active_event)

        async def stop_all():
            print("stop_all...")

            await asyncio.gather(
                stop_http_server(),
                stop_audio(),
                stop_whisper(),
                stop_grpc_server(),
            )

            print("stop_all done")

        signal.signal(signal.SIGINT, lambda signum, frame: asyncio.ensure_future(stop_all()))
        print("------------------- whisper_server running -------------------")

        # sleep forever by 1 hour intervals,
        # on Windows before Python 3.8 wake up every 1 second to handle
        # Ctrl+C smoothly
        if sys.platform == "win32":  # and sys.version_info < (3, 8):
            delay = 1
        else:
            delay = 3600

        while not interrupted_event.is_set():
            await asyncio.sleep(delay)

        print("interrupted_event must be set")
        # await stop_all()
    except (KeyboardInterrupt, SystemExit):
        print("Whisper main() interrupted by keyboard")
        pass

    print("DONE! end of main()")


def log_whisper(stt_results_queue: Queue):
    print("start log_whisper...")
    while True:
        try:
            alternatives = stt_results_queue.get()
            # print("app has " + str(len(list(alternatives))))
            print("app has " + str(len(alternatives)))
            for alternative in alternatives:
                print("  '" + str(alternative) + "'")
        except queue.Empty:
            print("empty stt_results queue")
            break

    print("exit log_whisper")


if __name__ == "__main__":
    # freeze_support()
    asyncio.run(main())
