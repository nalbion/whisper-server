from whisper_server.microphone import Microphone
from .service.openai_whisper_service import OpenAiWhisperService
from .service.whisper_x_service import WhisperxService
from .service.faster_whisper_service import FasterWhisperService


def main():
    mic = Microphone()
    # whisper = OpenAiWhisperService(mic)
    # whisper = WhisperxService(mic)
    whisper = FasterWhisperService(mic)

    mic.start()

    # TODO: initial prompt to provide context - words & named entities which are likely to be included in the speech
    # TODO: gain adjustable from client

    try:
        for results in whisper.run_speech_to_text():
            # print("app has " + str(len(list(results))))
            print("app has " + str(len(results)))
            for alternative in results:
                print("  '" + str(alternative) + "'")

    except KeyboardInterrupt:
        print("Whisper interrupted by keyboard")
        pass

    mic.stop()
