from abc import ABC, abstractmethod
import logging
import numpy as np


class AbstractWhisperService(ABC):
    def __init__(self, model: str = 'base', english: bool = True):
        self.logger = logging.getLogger('whisper_service')
        """
        Parameters
        model:   Whisper model size (tiny, base, small, medium, large)
        english: Use English-only model?
        """
        self.model_name = f'{model}{".en" if english else ""}'

    @abstractmethod
    def speech_to_text(self, audio: np.ndarray):
        pass
