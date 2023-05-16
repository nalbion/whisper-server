from abc import ABC, abstractmethod
import logging
import numpy as np


class AbstractWhisperService(ABC):
    def __init__(self, args):
        """
        Parameters
        model:   Whisper model size (tiny, base, small, medium, large)
        english: Use English-only model?
        """
        self.model_name = args.model

    @abstractmethod
    def speech_to_text(self, audio: np.ndarray):
        pass
