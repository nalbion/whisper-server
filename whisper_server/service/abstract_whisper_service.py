from abc import ABC, abstractmethod
import logging
import numpy as np
import signal
import multiprocessing

from whisper_server.microphone import Microphone

mic = Microphone()


# def signal_handler(signum: int, frame):  # FrameType | None):
#     print("Whisper process terminated")
#     mic.stop()
#
#
# def record_audio(audio_queue: multiprocessing.Queue):
#     for audio in mic.listen():
#         audio_queue.put(audio)
#     print("end record_audio")


class AbstractWhisperService(ABC):
    def __init__(self, model: str = 'base', english: bool = True):
        self.logger = logging.getLogger('whisper_service')
        """
        Parameters
        model:   Whisper model size (tiny, base, small, medium, large)
        english: Use English-only model?
        """
        self.model_name = f'{model}{".en" if english else ""}'
        # self.mic = mic
        # audio_queue = multiprocessing.Queue()
        # stt_results_queue = multiprocessing.Queue()
        # signal.signal(signal.SIGTERM, self.signal_handler)
        # self.audio_process = multiprocessing.Process(target=record_audio,
        #                                              args=(audio_queue,))
        # self.whisper_process = multiprocessing.Process(target=self.process_speech_to_text,
        #                                                args=(audio_queue, stt_results_queue))

    # def __del__(self):
    #     print("Whisper service clean up")
        # self.mic.stop()
        # self.whisper_process.terminate()
        # self.audio_process.terminate()

    # def process_speech_to_text(self,
    #                            audio_queue: multiprocessing.Queue,
    #                            stt_results_queue: multiprocessing.Queue):
    #     while True:
    #         audio = audio_queue.get()
    #         alternatives = self.speech_to_text(audio)
    #         alternatives = list(alternatives)
    #         if len(alternatives) != 0:
    #             stt_results_queue.put(alternatives)

    # TODO: probably needs to be run from a thread/coroutine?
    # The yield statement will suspend the process and return the yielded value.
    # When the subsequent next() function is called, the process is resumed until the following value is yielded.
    # def run_speech_to_text(self):
    #     for audio in self.mic.listen():
    #         alternatives = self.speech_to_text(audio)
    #         alternatives = list(alternatives)
    #         if len(alternatives) != 0:
    #             yield alternatives

    @abstractmethod
    def speech_to_text(self, audio: np.ndarray):
        pass
