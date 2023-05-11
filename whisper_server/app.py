from whisper_server.microphone import Microphone
from .service.openai_whisper_service import OpenAiWhisperService
from .service.whisper_x_service import WhisperxService
from .service.faster_whisper_service import FasterWhisperService


def main():
    mic = Microphone()
    # whisper = OpenAiWhisperService(mic, "base", True)
    # whisper = WhisperxService(mic)
    whisper = FasterWhisperService(mic)
    mic.start()

    for text in whisper.run_speech_to_text():
        print("app has text: '" + str(text) + "'")

    mic.stop()
