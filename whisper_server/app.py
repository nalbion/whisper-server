from whisper_server.microphone import Microphone
from .service.abstract_whisper_service import AbstractWhisperService
from .service.openai_whisper_service import OpenAiWhisperService
from .service.whisper_x_service import WhisperxService
from .service.faster_whisper_service import FasterWhisperService
from .server import Server

def main():
    mic = Microphone()

    whisper = start_whisper(mic)

    # log_whisper(whisper)

    # TODO: initial prompt to provide context - words & named entities which are likely to be included in the speech
    # TODO: gain adjustable from client

    run_server(whisper)

    mic.stop()


def start_whisper(mic: Microphone) -> AbstractWhisperService:
    # whisper = OpenAiWhisperService(mic)
    # whisper = WhisperxService(mic)
    whisper = FasterWhisperService(mic)

    mic.start()
    return whisper

def log_whisper(whisper: AbstractWhisperService):
    try:
        for results in whisper.run_speech_to_text():
            # print("app has " + str(len(list(results))))
            print("app has " + str(len(results)))
            for alternative in results:
                print("  '" + str(alternative) + "'")

    except KeyboardInterrupt:
        print("Whisper interrupted by keyboard")
        pass


def run_server(whisper: AbstractWhisperService):
    server = Server()

    server.startHttp()
    # server.start_discoverability()
    # return server

    # server.use_whisper(whisper)

    # server.stop_discoverability()
