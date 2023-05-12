from abc import ABC, abstractmethod
import logging
import numpy as np

from whisper_server.microphone import Microphone


class AbstractWhisperService(ABC):
    def __init__(self, mic: Microphone, model: str = 'base', english: bool = True):
        self.logger = logging.getLogger('whisper_service')
        """
        Parameters
        model:   Whisper model size (tiny, base, small, medium, large)
        english: Use English-only model?
        """
        self.model_name = f'{model}{".en" if english else ""}'
        self.mic = mic
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def __del__(self):
        self.mic.stop()

    # TODO: probably needs to be run from a thread/coroutine?
    # The yield statement will suspend the process and return the yielded value.
    # When the subsequent next() function is called, the process is resumed until the following value is yielded.
    def run_speech_to_text(self):
        for audio in self.mic.listen():
            alternatives = self.speech_to_text(audio)
            alternatives = list(alternatives)
            if len(alternatives) != 0:
                yield alternatives

    @abstractmethod
    def speech_to_text(self, audio: np.ndarray):
        pass
