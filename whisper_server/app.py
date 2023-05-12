import threading

from whisper_server.microphone import Microphone
from .service.abstract_whisper_service import AbstractWhisperService
from .service.openai_whisper_service import OpenAiWhisperService
from .service.whisper_x_service import WhisperxService
from .service.faster_whisper_service import FasterWhisperService
from .server import Server, use_whisper

def main():
    mic = Microphone()
    try:
        whisper = start_whisper(mic)
        # log_whisper(whisper)

        # TODO: initial prompt to provide context - words & named entities which are likely to be included in the speech
        # TODO: gain adjustable from client
        run_server(whisper)
    except KeyboardInterrupt:
        print("Whisper interrupted by keyboard")
        pass

    mic.stop()


def start_whisper(mic: Microphone) -> AbstractWhisperService:
    # whisper = OpenAiWhisperService(mic)
    # whisper = WhisperxService(mic)
    whisper = FasterWhisperService(mic)

    mic.start()
    return whisper


def log_whisper(whisper: AbstractWhisperService):
    for results in whisper.run_speech_to_text():
        # print("app has " + str(len(list(results))))
        print("app has " + str(len(results)))
        for alternative in results:
            print("  '" + str(alternative) + "'")


def run_server(whisper: AbstractWhisperService):
    use_whisper(whisper)
    server = Server()

    # thread = threading.Thread(target=server.startHttp)
    # thread.start()
    server.start_http()

    # server.start_discoverability()
    # return server

    # server.stop_discoverability()
