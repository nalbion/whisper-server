import os

import asyncio
from threading import Thread
from multiprocessing import Process, Queue, Event
import signal
import sys
import queue
# import pcntl
import socket
import pyaudio
from whisper_server.microphone import Microphone

# from whisper_server.service.abstract_whisper_service import AbstractWhisperService
from whisper_server.service.openai_whisper_service import OpenAiWhisperService
# from whisper_server.service.whisper_x_service import WhisperxService
from whisper_server.service.faster_whisper_service import FasterWhisperService
from whisper_server.http_server import HttpServer, use_results_queue
# from whisper_server.grpc_server import GrpcServer


def start_audio_process(audio_queue: Queue):
    mic = Microphone()
    mic.start()

    def process_record_audio():  # audio_queue: multiprocessing.Queue):
        print("process_record_audio starting...")
        mic.start()

        for audio in mic.listen():
            print("received audio, putting to queue")
            audio_queue.put(audio)

        print("  exit process_record_audio...")

    audio_process = Process(name="whisper_server audio", target=process_record_audio)  # , args=(audio_queue,))

    async def stop():
        print("stopping audio process")
        mic.stop()
        mic.close()
        audio_queue.close()
        audio_queue.cancel_join_thread()
        audio_process.terminate()
        audio_process.join()
        # del mic
        print("  audio process stopped")

    return stop


def start_audio_thread(audio_queue: Queue, audio_active_event: Event):
    mic = Microphone()

    if audio_active_event.is_set():
        mic.start()

    def run_audio_loop():
        print("start run_audio_loop")
        if not audio_active_event.is_set():
            mic.stop()
            print("waiting for startRecognition()")
            audio_active_event.wait()
            mic.start()

        # TODO: this should exit and restart the loop on stopRecognition()
        for audio in mic.listen():
            audio_queue.put(audio)

        print("  exit run_audio_loop")

    audio_thread = Thread(name="whisper_server audio", target=run_audio_loop)
    audio_thread.start()

    async def stop():
        print("stopping audio thread")
        mic.stop()
        mic.close()
        audio_queue.close()
        audio_queue.cancel_join_thread()
        audio_thread.join()
        # del mic
        print("  audio thread stopped")

    return stop


def signal_handler(interrupted_event):
    print("run_whisper_loop Received SIGINT signal")
    interrupted_event.set()
    # _audio_queue.close()
    # _stt_results_queue.put(signal)
    # _stt_results_queue.close()
    # _stt_results_queue.cancel_join_thread()
    # sys.exit(0)


def run_whisper_loop(_audio_queue: Queue, _stt_results_queue: Queue, interrupted_event: Event):
    print("run_whisper_loop starting...")
    # whisper = OpenAiWhisperService(audio_queue)
    # whisper = WhisperxService(audio_queue)
    whisper = FasterWhisperService()

    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(interrupted_event))
    # pcntl.signal(pcntl.SIGINT, signal_handler)

    while True:
        try:
            audio = _audio_queue.get()
            # if audio == "stop":
            #     print("process_speech_to_text received 'stop'")
            #     break
            alternatives = whisper.speech_to_text(audio)
            alternatives = list(alternatives)
            if len(alternatives) != 0:
                _stt_results_queue.put(alternatives)
        except ValueError:
            print("  ValueError in reading from audio_queue")
            break
        except queue.Empty:
            print("empty audio queue")
            break
        except (KeyboardInterrupt, InterruptedError, SystemExit):
            _audio_queue.close()
            _audio_queue.cancel_join_thread()
            _stt_results_queue.close()
            _stt_results_queue.cancel_join_thread()
            print("  run_whisper_loop process interrupted by keyboard")
            break

    print("  exit process_speech_to_text")


def start_whisper_process(audio_queue: Queue, stt_results_queue: Queue, interrupted_event: Event):
    print("starting whisper_process...")
    # interrupted_event = Event()
    whisper_process = Process(name="whisper_server speech to text",
                              target=run_whisper_loop,
                              args=(audio_queue, stt_results_queue, interrupted_event),
                              # daemon=True
                              )
    whisper_process.start()

    # os.killpg(os.getpgid(whisper_process.pid), signal.SIGINT)

    async def stop():
        print("terminating whisper_process")
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_process.terminate()
        whisper_process.join()
        print("  start_whisper_process.stop() terminated whisper_process")

    return stop, interrupted_event


def start_whisper_thread(audio_queue: Queue, stt_results_queue: Queue):
    print("starting whisper_thread...")
    whisper_thread = Thread(name="whisper_server speech to text",
                            target=run_whisper_loop,
                            args=(audio_queue, stt_results_queue))
    whisper_thread.start()

    async def stop():
        print("terminating whisper_thread")
        # terminate is more graceful than kill (abort)
        # audio_queue.put("stop")
        audio_queue.close()
        audio_queue.cancel_join_thread()
        stt_results_queue.close()
        stt_results_queue.cancel_join_thread()
        whisper_thread.join()
        print("  start_whisper_thread.stop() terminated whisper_thread")

    return stop


def start_http_server_thread(stt_results_queue: Queue):
    server = HttpServer()

    def run_server():  # stt_results_queue: Queue):
        print("run_server starting...")
        use_results_queue(stt_results_queue)

        # thread = Thread(target=server.startHttp)
        # thread.start()
        server.start_http()

        # server.start_discoverability()
        # return server

        # server.stop_discoverability()
        print("  exit run_server")

    server_thread = Thread(name="whisper_server server", target=run_server)
    server_thread.start()

    async def stop():
        print("stopping http_server_thread...")
        server.stop_http()
        server.stop_discoverability()
        server_thread.join()
        print("  server thread stopped")

    return stop


def start_grpc_server(stt_results_queue: Queue, audio_active_event: Event):
    print("starting grpc_server...")
    server = GrpcServer(stt_results_queue, audio_active_event)
    server.start()

    async def stop():
        print("stopping grpc_server_thread...")
        server.stop()
        print("  grpc_server_thread stopped")

    return stop()


def not_started(name: str):
    # return lambda: print(f"{name} not started")
    async def print_not_started():
        print(f"{name} not started")

    return print_not_started


async def main():
    # signal.signal(signal.SIGINT, signal.SIG_IGN)

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
        print("start main()")
        stop_audio = start_audio_thread(audio_queue, audio_active_event)
        stop_whisper = start_whisper_process(audio_queue, stt_results_queue, interrupted_event)
        # stop_whisper = start_whisper_thread(audio_queue, stt_results_queue)

        if True:
            audio_active_event.set()
            log_whisper(stt_results_queue)
            stop_http_server = start_http_server_thread(stt_results_queue)
        else:
            stop_grpc_server = start_grpc_server(stt_results_queue, audio_active_event)

        async def stop_all(signum: int, frame):
            print("stop_all...")
            # stop_http_server()
            # stop_audio()
            # stop_whisper()
            await asyncio.gather(
                stop_http_server(),
                stop_audio(),
                stop_whisper(),
                stop_grpc_server(),
            )
            running = False
            print("stop_all done")

        # signal.signal(signal.SIGINT, stop_all)
        print("------------------- whisper_server running -------------------")

        # sleep forever by 1 hour intervals,
        # on Windows before Python 3.8 wake up every 1 second to handle
        # Ctrl+C smoothly
        # if sys.platform == "win32" and sys.version_info < (3, 8):
        #     delay = 1
        # else:
        #     delay = 3600
        delay = 1

        while not interrupted_event.is_set():
            await asyncio.sleep(delay)

        print("interrupted_event must be set")
    except (KeyboardInterrupt, SystemExit):
        print("Whisper main() interrupted by keyboard")
        pass

    # print("waiting for ctrl+c")
    # # signal.sigwait({signal.SIGINT, signal.SIGTERM})
    # print("interrupted")

    # print("stopping...")
    # await asyncio.gather(
    #     stop_http_server(),
    #     stop_audio(),
    #     stop_whisper(),
    # )

    # await stop_http_server()
    # await stop_audio()
    # await stop_whisper()

    print("DONE! end of main()")


# def start_whisper() -> AbstractWhisperService:
#     # whisper = OpenAiWhisperService()
#     # whisper = WhisperxService()
#     whisper = FasterWhisperService()
#     #
#     # mic.start()
#     return whisper


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


# def signal_handler(signum: int, frame):  # FrameType | None):
#     print("signal_handler stopping mic")
#     # mic.stop()
#     print("whisper_server process terminated")
#
#
# signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # freeze_support()
    asyncio.run(main())
